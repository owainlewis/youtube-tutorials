import unittest
from domain import begin_incident, finish_incident


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.event = {'incident_id': 'test', 'state': 'open', 'started_at': 1700000000,
                      'policy_name': 'Checkout errors'}
        self.clock = '2026-09-16T12:00:00+00:00'

    def test_open_duplicate_does_not_start_second_investigation(self):
        record, run = begin_incident(None, self.event, self.clock)
        self.assertTrue(run)
        self.assertEqual(record['status'], 'investigating')
        duplicate, run = begin_incident(record, self.event, self.clock)
        self.assertFalse(run)
        self.assertEqual(duplicate, record)

    def test_expired_work_is_retried(self):
        record, _ = begin_incident(None, self.event, self.clock)
        _, run = begin_incident(record, self.event, '2026-09-16T12:05:00+00:00')
        self.assertTrue(run)

    def test_failed_work_is_retried(self):
        record, _ = begin_incident(None, self.event, self.clock)
        record = finish_incident(record, error='Model unavailable')
        _, run = begin_incident(record, self.event)
        self.assertTrue(run)

    def test_success_is_not_repeated(self):
        record, _ = begin_incident(None, self.event, self.clock)
        record = finish_incident(record, report={'likely_cause': 'Regression'})
        _, run = begin_incident(record, self.event)
        self.assertFalse(run)

    def test_close_arriving_first_is_terminal(self):
        closed = dict(self.event, state='closed', ended_at=1700000120)
        record, run = begin_incident(None, closed, self.clock)
        self.assertFalse(run)
        self.assertEqual(record['status'], 'recovered')
        record, run = begin_incident(record, self.event, self.clock)
        self.assertFalse(run)
        self.assertEqual(record['state'], 'closed')

    def test_late_report_preserves_recovery(self):
        record, _ = begin_incident(None, dict(self.event, state='closed'), self.clock)
        report = {'likely_cause': 'Regression'}
        result = finish_incident(record, report)
        self.assertEqual(result['status'], 'recovered')
        self.assertEqual(result['report'], report)

    def test_late_error_cannot_replace_recovery(self):
        record, _ = begin_incident(None, dict(self.event, state='closed'), self.clock)
        result = finish_incident(record, error='Timeout')
        self.assertEqual(result['status'], 'recovered')


if __name__ == '__main__':
    unittest.main()
