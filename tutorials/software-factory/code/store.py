"""Firestore keeps incident state across Cloud Run restarts and duplicate deliveries."""
import os
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from domain import begin_incident, finish_incident, incident_key, now


class IncidentStore:
    def __init__(self):
        self.db = firestore.Client(project=os.environ['GOOGLE_CLOUD_PROJECT'],
                                   database=os.getenv('FIRESTORE_DATABASE', 'software-factory'))
        self.collection = self.db.collection('incidents')

    def ref(self, incident_id):
        return self.collection.document(incident_key(incident_id))

    def begin(self, incident):
        ref = self.ref(incident['incident_id'])

        @firestore.transactional
        def update(transaction):
            snapshot = ref.get(transaction=transaction)
            record, run = begin_incident(snapshot.to_dict() if snapshot.exists else None, incident)
            from urllib.parse import quote
            project = os.environ['GOOGLE_CLOUD_PROJECT']
            record['url'] = ('https://console.cloud.google.com/monitoring/alerting/incidents/'
                             + quote(incident['incident_id'], safe='') + '?project=' + project)
            transaction.set(ref, record)
            return record, run
        return update(self.db.transaction())

    def step(self, incident_id, tool):
        self.ref(incident_id).update({'steps': firestore.ArrayUnion([
            {'at': now(), 'tool': tool, 'status': 'complete'}])})

    def finish(self, incident_id, report=None, error=None):
        ref = self.ref(incident_id)

        @firestore.transactional
        def update(transaction):
            record = ref.get(transaction=transaction).to_dict()
            transaction.set(ref, finish_incident(record, report, error))
        update(self.db.transaction())

    def list(self):
        active = [doc.to_dict() for doc in self.collection.where(
            filter=FieldFilter('state', '==', 'open')).stream()]
        recent = [doc.to_dict() for doc in self.collection.order_by(
            'started_at', direction=firestore.Query.DESCENDING).limit(30).stream()]
        return sorted(active + [item for item in recent if item.get('state') == 'closed'],
                      key=lambda item: item['started_at'], reverse=True)
