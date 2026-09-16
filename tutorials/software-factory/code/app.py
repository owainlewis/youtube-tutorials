"""One image, three services: demo API, private worker, read-only dashboard."""
import asyncio
import base64
import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

MODE = os.getenv('APP_MODE', 'api')
SERVICE = os.getenv('TARGET_SERVICE', 'software-factory-api')
app = FastAPI(title='Software Factory ' + MODE)


@lru_cache
def store():
    from store import IncidentStore
    return IncidentStore()


@app.get('/healthz')
def health():
    return {'status': 'ok', 'mode': MODE}


class Checkout(BaseModel):
    product_id: str = Field(default='course', max_length=80)
    quantity: int = Field(default=1, ge=1, le=10)


if MODE == 'api':
    @app.get('/api/products')
    def products():
        return {'products': [{'id': 'course', 'name': 'AI Engineer demo course', 'price_gbp': 49}]}

    @app.post('/api/checkout')
    def checkout(order: Checkout):
        if order.product_id != 'course':
            raise HTTPException(404, 'Product not found')
        revision = os.getenv('K_REVISION', 'local')
        # A revision-level fault reproduces a bad release without an exposed admin switch.
        if os.getenv('DEMO_FAILURE', 'false').lower() == 'true':
            print(json.dumps({'severity': 'ERROR', 'message': 'Checkout failed: price lookup returned None',
                              'error_type': 'PriceLookupError', 'endpoint': '/api/checkout',
                              'revision': revision}), flush=True)
            return JSONResponse({'error': 'Checkout temporarily unavailable', 'revision': revision}, status_code=500)
        return {'status': 'accepted', 'total_gbp': order.quantity * 49, 'revision': revision,
                'note': 'Synthetic demo. No payment or order is stored.'}

elif MODE == 'dashboard':
    @app.get('/')
    def dashboard():
        return FileResponse(Path(__file__).parent / 'static' / 'index.html',
                            headers={'Cache-Control': 'no-store'})

    @app.get('/api/incidents')
    def incidents():
        return JSONResponse({'incidents': store().list(), 'service': SERVICE},
                            headers={'Cache-Control': 'no-store'})

elif MODE == 'worker':
    @app.post('/events')
    async def receive(request: Request):
        # Cloud Run IAM authenticates Pub/Sub before the application sees a request.
        try:
            envelope = await request.json()
            encoded = envelope['message']['data']
            if len(encoded) > 100_000:
                raise ValueError('Event too large')
            payload = json.loads(base64.b64decode(encoded, validate=True))
            incident = payload['incident']
            if incident['state'] not in ('open', 'closed'):
                raise ValueError('Invalid incident state')
            if not isinstance(incident['incident_id'], str) or not incident['incident_id']:
                raise ValueError('Missing incident ID')
            datetime.fromtimestamp(float(incident['started_at']), timezone.utc)
            if incident.get('ended_at'):
                datetime.fromtimestamp(float(incident['ended_at']), timezone.utc)
        except (ValueError, KeyError, TypeError, OverflowError, OSError):
            raise HTTPException(400, 'Invalid Monitoring Pub/Sub notification')
        expected_project = os.environ['GOOGLE_CLOUD_PROJECT']
        resource = incident.get('resource', {})
        labels = resource.get('labels', {})
        if (labels.get('service_name') != SERVICE or
                labels.get('project_id') != expected_project):
            # Acknowledge unrelated events without making a model call.
            return {'ignored': True}
        db = store()
        record, run = await asyncio.to_thread(db.begin, incident)
        if not run:
            if record.get('status') == 'investigating':
                # Retry rather than ACK while another invocation owns a lease.
                raise HTTPException(503, 'Investigation already running')
            return {'status': record['status']}
        try:
            from agent import investigate
            report = await asyncio.wait_for(investigate(incident, db), timeout=180)
            await asyncio.to_thread(db.finish, incident['incident_id'], report=report)
        except Exception:
            # Do not expose SDK exceptions or raw operational data in the public error field.
            import logging
            logging.exception('Triage failed')
            await asyncio.to_thread(db.finish, incident['incident_id'],
                                    error='Investigation failed. Check worker logs; delivery will retry.')
            raise HTTPException(503, 'Investigation failed')
        return {'status': 'triaged'}
else:
    raise RuntimeError('APP_MODE must be api, worker or dashboard')
