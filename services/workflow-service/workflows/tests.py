from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from django.test import SimpleTestCase
from graphql import GraphQLError

from workflows.consumer import _process_event_with_retries
from workflows.handler import InMemoryStateStore, LeadCreatedHandler
from workflows.schema import resolve_workflow_events


class WorkflowHandlerTests(SimpleTestCase):
    def test_duplicate_completed_event_is_skipped(self):
        state_store = InMemoryStateStore(records={"event-1": {"status": "COMPLETED"}})
        crm_client = Mock()
        logger = Mock()
        handler = LeadCreatedHandler(state_store, crm_client, logger)

        result = handler.handle({"eventId": "event-1", "leadId": "lead-1"})

        self.assertEqual(result, "duplicate")
        crm_client.assert_not_called()

    def test_event_marks_completion(self):
        state_store = InMemoryStateStore(records={})
        crm_client = Mock()
        logger = Mock()
        handler = LeadCreatedHandler(state_store, crm_client, logger)

        handler.handle({"eventId": "event-2", "leadId": "44444444-4444-4444-8444-444444444441"})

        self.assertEqual(state_store.records["event-2"]["status"], "COMPLETED")
        crm_client.assert_called_once()


class WorkflowConsumerRetryTests(SimpleTestCase):
    def test_process_event_retries_until_success(self):
        handler = Mock()
        handler.handle = Mock(side_effect=[RuntimeError("temporary"), "completed"])
        payload = {"eventId": "event-3", "leadId": "lead-3"}

        with patch("workflows.consumer.time.sleep") as sleep:
            result = _process_event_with_retries(handler, payload, max_retries=3, base_delay_seconds=1)

        self.assertEqual(result, "completed")
        self.assertEqual(handler.handle.call_count, 2)
        sleep.assert_called_once_with(1)

    def test_process_event_raises_after_max_retries(self):
        handler = Mock()
        handler.handle = Mock(side_effect=RuntimeError("permanent"))
        payload = {"eventId": "event-4", "leadId": "lead-4"}

        with patch("workflows.consumer.time.sleep") as sleep:
            with self.assertRaises(RuntimeError):
                _process_event_with_retries(handler, payload, max_retries=3, base_delay_seconds=1)

        self.assertEqual(handler.handle.call_count, 3)
        self.assertEqual(sleep.call_args_list, [call(1), call(2)])


class WorkflowSchemaGuardTests(SimpleTestCase):
    def test_workflow_events_requires_internal_token(self):
        info = SimpleNamespace(context=SimpleNamespace(headers={}))

        with self.assertRaisesMessage(GraphQLError, "Internal service token required."):
            resolve_workflow_events(None, info)
