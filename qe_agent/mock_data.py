"""
Module 1B - Mock Data Generator.
Tạo fake tickets cover edge case của từng rule.
Person 2 dùng cái này để dev rules engine, KHÔNG phải chờ Jira xong.

Run:  python -m qe_agent.mock_data        # in ra JSON
"""
from __future__ import annotations
import json
from datetime import date, timedelta
from .models import Ticket

TODAY = date.today()
def d(offset: int) -> date:
    return TODAY + timedelta(days=offset)


def generate_mock_tickets() -> list[Ticket]:
    """Mỗi ticket được thiết kế để trigger 1 edge case cụ thể."""
    return [
        # --- Simple filters (checklists) ---
        Ticket("PROJ-1", "Login API needs test start today", "Ready for testing",
               3, test_start_date=TODAY, test_complete_date=d(3),
               sandbox_date=d(5), assignee="alice", qe_pic="qe_bob",
               component="Marketing Solutions"),
        Ticket("PROJ-2", "Checkout must complete test today", "InTest",
               5, test_start_date=d(-2), test_complete_date=TODAY,
               sandbox_date=d(2), assignee="carol", qe_pic="qe_bob",
               component="CRM"),
        Ticket("PROJ-3", "Payment sandbox tomorrow", "InTest",
               5, test_start_date=d(-3), test_complete_date=d(1),
               sandbox_date=d(1), assignee="dave", qe_pic="qe_eve",
               component="Marketing Solutions"),
        Ticket("PROJ-4", "Search blocked ticket", "Blocked",
               2, test_start_date=d(-1), test_complete_date=d(2),
               sandbox_date=d(4), assignee="frank", qe_pic="qe_eve",
               blocked=True, component=None),  # không MS/CRM -> cả hai Dev

        # --- Level 1 Violent ---
        # L1_START_TODAY_WRONG_STATUS: test_start_date==today, status còn InDev
        Ticket("PROJ-5", "Start date today but still InDev", "InDev",
               3, test_start_date=TODAY, test_complete_date=d(2),
               sandbox_date=d(4), assignee="grace", qe_pic="qe_bob"),
        # L1_TEST_COMPLETE_OVERDUE: test_complete_date < today, status InTest
        Ticket("PROJ-6", "Test complete overdue", "InTest",
               8, test_start_date=d(-5), test_complete_date=d(-1),
               sandbox_date=d(3), assignee="heidi", qe_pic="qe_eve"),
        # L1_TOO_MANY_SAME_TEST_START: >3 tickets cùng start date + qe_pic (qe_bob: 1,5,7,8 = 4)
        Ticket("PROJ-7", "Same start date #2", "Ready for testing",
               2, test_start_date=TODAY, test_complete_date=d(3),
               sandbox_date=d(5), assignee="ivan", qe_pic="qe_bob"),
        Ticket("PROJ-8", "Same start date #3", "Ready for testing",
               2, test_start_date=TODAY, test_complete_date=d(3),
               sandbox_date=d(5), assignee="judy", qe_pic="qe_bob"),
        Ticket("PROJ-9", "Same start date #4", "Ready for testing",
               2, test_start_date=TODAY, test_complete_date=d(3),
               sandbox_date=d(5), assignee="ken", qe_pic="qe_bob"),
        # L1_SANDBOX_DATE_WRONG_STATUS: sandbox_date==today, status InDev (chưa Walkthrough)
        Ticket("PROJ-10", "Sandbox date but still InDev", "InDev",
               5, test_start_date=d(-3), test_complete_date=d(1),
               sandbox_date=TODAY, assignee="laura", qe_pic="qe_bob"),

        # --- Level 2 Risk (story point + complete date) ---
        # L2_OVERDUE_STILL_INREVIEW: test_complete_date < today, status InReview
        Ticket("PROJ-11", "Overdue still InReview", "InReview",
               13, test_start_date=d(-5), test_complete_date=d(-1),
               sandbox_date=d(3), assignee="mike", qe_pic="qe_eve"),
        # L2_DUE_TODAY_SP3_NOT_TESTING: test_complete_date==today, SP=3, status InDev
        Ticket("PROJ-12", "Due today SP3 not in test", "InDev",
               3, test_start_date=d(-2), test_complete_date=TODAY,
               sandbox_date=d(4), assignee="nina", qe_pic="qe_bob"),

        # --- Level 3 Warning ---
        # L3_DUE_TODAY_SP3_IN_TEST: test_complete_date==today, SP=3, status InTest
        Ticket("PROJ-13", "Due today SP3 InTest", "InTest",
               3, test_start_date=d(-2), test_complete_date=TODAY,
               sandbox_date=d(2), assignee="oscar", qe_pic="qe_eve"),
        # L3_PRE_SANDBOX_1DAY_SP5_NOT_INDEV: sandbox=tomorrow, SP=5, status Reviewed
        Ticket("PROJ-14", "Sandbox tomorrow SP5 not InDev", "Reviewed",
               5, test_start_date=d(1), test_complete_date=d(3),
               sandbox_date=d(1), assignee="peggy", qe_pic="qe_bob"),

        # --- NoQE flag + bug ---
        Ticket("PROJ-15", "NoQE bug ticket", "InTest",
               3, test_start_date=TODAY, test_complete_date=d(2),
               sandbox_date=d(4), assignee="quinn", qe_pic=None,
               no_qe=True, is_bug=True),
    ]


def _serialize(t: Ticket) -> dict:
    def iso(x): return x.isoformat() if x else None
    return {
        "id": t.id, "title": t.title, "status": t.status,
        "story_point": t.story_point,
        "test_start_date": iso(t.test_start_date),
        "test_complete_date": iso(t.test_complete_date),
        "sandbox_date": iso(t.sandbox_date),
        "assignee": t.assignee, "qe_pic": t.qe_pic,
        "no_qe": t.no_qe, "blocked": t.blocked, "is_bug": t.is_bug,
    }


if __name__ == "__main__":
    print(json.dumps([_serialize(t) for t in generate_mock_tickets()],
                     indent=2, ensure_ascii=False))
