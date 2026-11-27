import datetime

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Sprint, Ticket

User = get_user_model()


class TicketApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@test.com', password='x', name='Admin', is_staff=True
        )
        self.employee = User.objects.create_user(
            email='emp@test.com', password='x', name='Employee'
        )
        today = datetime.date.today()
        self.active = Sprint.objects.create(
            name='S1', start_date=today, end_date=today, created_by=self.admin
        )
        self.closed = Sprint.objects.create(
            name='S0', start_date=today, end_date=today, created_by=self.admin,
            status=Sprint.Status.CLOSED,
        )
        self.ticket = Ticket.objects.create(
            title='Existing', estimation=1, priority='low',
            assignee=self.employee, creator=self.admin,
        )
        self.list_url = '/api/tickets/'
        self.detail_url = f'/api/tickets/{self.ticket.id}/'
        self.valid = {
            'title': 'Fix login', 'description': 'details', 'estimation': 3,
            'priority': 'high', 'assignee': str(self.employee.id),
        }

    # --- authentication / authorization
    def test_unauthenticated_is_rejected(self):
        self.assertEqual(self.client.get(self.list_url).status_code, 401)

    def test_employee_can_read(self):
        self.client.force_authenticate(self.employee)
        self.assertEqual(self.client.get(self.list_url).status_code, 200)
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)
        self.assertEqual(self.client.get(self.list_url + 'backlog/').status_code, 200)

    def test_employee_cannot_write(self):
        self.client.force_authenticate(self.employee)
        self.assertEqual(self.client.post(self.list_url, self.valid).status_code, 403)
        self.assertEqual(self.client.put(self.detail_url, self.valid).status_code, 403)
        self.assertEqual(self.client.patch(self.detail_url, {'title': 'x'}).status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)

    def test_admin_full_crud(self):
        self.client.force_authenticate(self.admin)
        created = self.client.post(self.list_url, self.valid)
        self.assertEqual(created.status_code, 201)
        url = f"/api/tickets/{created.data['id']}/"
        self.assertEqual(self.client.patch(url, {'priority': 'low'}).status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)

    # --- creator
    def test_creator_is_set_from_authenticated_user(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.list_url, self.valid)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(response.data['creator']), str(self.admin.id))

    def test_creator_cannot_be_overwritten_by_client(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.list_url, {**self.valid, 'creator': str(self.employee.id)}
        )
        self.assertEqual(str(response.data['creator']), str(self.admin.id))
        patched = self.client.patch(self.detail_url, {'creator': str(self.employee.id)})
        self.assertEqual(str(patched.data['creator']), str(self.admin.id))

    # --- validation
    def test_assignee_is_optional(self):
        self.client.force_authenticate(self.admin)
        data = {k: v for k, v in self.valid.items() if k != 'assignee'}
        self.assertEqual(self.client.post(self.list_url, data).status_code, 201)

    def test_nonexistent_assignee_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.list_url, {**self.valid, 'assignee': '00000000-0000-0000-0000-000000000000'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('assignee', response.data)

    def test_negative_estimation_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.list_url, {**self.valid, 'estimation': -1})
        self.assertEqual(response.status_code, 400)
        self.assertIn('estimation', response.data)

    def test_invalid_priority_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.list_url, {**self.valid, 'priority': 'urgent'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('priority', response.data)

    def test_missing_ticket_returns_404(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/api/tickets/00000000-0000-0000-0000-000000000000/')
        self.assertEqual(response.status_code, 404)

    # --- sprint / backlog
    def test_ticket_without_sprint_is_backlog(self):
        self.assertTrue(self.ticket.is_backlog)

    def test_cannot_create_ticket_in_closed_sprint(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(self.list_url, {**self.valid, 'sprint': str(self.closed.id)})
        self.assertEqual(response.status_code, 400)
        self.assertIn('sprint', response.data)

    def test_cannot_move_ticket_into_closed_sprint(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(self.detail_url, {'sprint': str(self.closed.id)})
        self.assertEqual(response.status_code, 400)

    def test_ticket_already_in_closed_sprint_stays_editable(self):
        ticket = Ticket.objects.create(
            title='Old', estimation=1, priority='low', creator=self.admin, sprint=self.closed
        )
        self.client.force_authenticate(self.admin)
        response = self.client.patch(f'/api/tickets/{ticket.id}/', {'title': 'Renamed'})
        self.assertEqual(response.status_code, 200)

    def test_admin_moves_ticket_between_backlog_and_sprint(self):
        self.client.force_authenticate(self.admin)
        to_sprint = self.client.patch(self.detail_url, {'sprint': str(self.active.id)})
        self.assertEqual(to_sprint.status_code, 200)
        back = self.client.patch(self.detail_url, {'sprint': None}, format='json')
        self.assertEqual(back.status_code, 200)
        self.assertIsNone(back.data['sprint'])

    def test_backlog_returns_only_tickets_without_sprint(self):
        Ticket.objects.create(
            title='In sprint', estimation=1, priority='low', creator=self.admin, sprint=self.active
        )
        self.client.force_authenticate(self.employee)
        response = self.client.get(self.list_url + 'backlog/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Existing')

    def test_deleting_sprint_moves_tickets_to_backlog(self):
        ticket = Ticket.objects.create(
            title='In sprint', estimation=1, priority='low', creator=self.admin, sprint=self.active
        )
        self.active.delete()
        ticket.refresh_from_db()
        self.assertIsNone(ticket.sprint)

    # --- list / filters
    def test_list_is_paginated(self):
        self.client.force_authenticate(self.employee)
        response = self.client.get(self.list_url)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_filters(self):
        Ticket.objects.create(
            title='High one', estimation=2, priority='high',
            assignee=self.admin, creator=self.admin, sprint=self.active,
        )
        self.client.force_authenticate(self.employee)
        self.assertEqual(self.client.get(self.list_url, {'priority': 'high'}).data['count'], 1)
        self.assertEqual(
            self.client.get(self.list_url, {'assignee': str(self.employee.id)}).data['count'], 1
        )
        self.assertEqual(
            self.client.get(self.list_url, {'sprint': str(self.active.id)}).data['count'], 1
        )

class SprintApiTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='x',
            name='Admin',
            is_staff=True
        )

        self.employee = User.objects.create_user(
            email='employee@test.com',
            password='x',
            name='Employee'
        )

        today = datetime.date.today()

        self.sprint = Sprint.objects.create(
            name='Sprint 1',
            description='First sprint',
            start_date=today,
            end_date=today + datetime.timedelta(days=14),
            created_by=self.admin
        )

        self.list_url = '/api/sprints/'
        self.detail_url = f'/api/sprints/{self.sprint.id}/'

        self.valid = {
            'name': 'Sprint 2',
            'description': 'New sprint',
            'start_date': str(today + datetime.timedelta(days=15)),
            'end_date': str(today + datetime.timedelta(days=29)),
            'status': Sprint.Status.ACTIVE
        }

    # --- authentication

    def test_unauthenticated_is_rejected(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            401
        )

    # --- authorization

    def test_employee_can_read(self):
        self.client.force_authenticate(
            self.employee
        )

        self.assertEqual(
            self.client.get(self.list_url).status_code,
            200
        )

        self.assertEqual(
            self.client.get(self.detail_url).status_code,
            200
        )

    def test_employee_cannot_create(self):
        self.client.force_authenticate(
            self.employee
        )

        self.assertEqual(
            self.client.post(
                self.list_url,
                self.valid
            ).status_code,
            403
        )

    def test_employee_cannot_update(self):
        self.client.force_authenticate(
            self.employee
        )

        self.assertEqual(
            self.client.patch(
                self.detail_url,
                {'name': 'Changed'}
            ).status_code,
            403
        )

    def test_employee_cannot_delete(self):
        self.client.force_authenticate(
            self.employee
        )

        self.assertEqual(
            self.client.delete(
                self.detail_url
            ).status_code,
            403
        )

    # --- CRUD

    def test_admin_can_create_sprint(self):
        self.client.force_authenticate(
            self.admin
        )

        response = self.client.post(
            self.list_url,
            self.valid
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_admin_can_update_sprint(self):
        self.client.force_authenticate(
            self.admin
        )

        response = self.client.patch(
            self.detail_url,
            {'name': 'Updated Sprint'}
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_admin_can_delete_sprint(self):
        self.client.force_authenticate(
            self.admin
        )

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            204
        )

    # --- creator

    def test_creator_is_set_from_authenticated_user(self):
        self.client.force_authenticate(
            self.admin
        )

        response = self.client.post(
            self.list_url,
            self.valid
        )

        self.assertEqual(
            str(response.data['created_by']),
            str(self.admin.id)
        )

    def test_creator_cannot_be_overwritten(self):
        self.client.force_authenticate(
            self.admin
        )

        response = self.client.post(
            self.list_url,
            {
                **self.valid,
                'created_by': str(self.employee.id)
            }
        )

        self.assertEqual(
            str(response.data['created_by']),
            str(self.admin.id)
        )

    # --- validation

    def test_invalid_dates_rejected(self):
        self.client.force_authenticate(
            self.admin
        )

        response = self.client.post(
            self.list_url,
            {
                **self.valid,
                'start_date': '2026-12-20',
                'end_date': '2026-12-01'
            }
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # --- filters

    def test_filter_by_status(self):
        Sprint.objects.create(
            name='Closed Sprint',
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=14),
            created_by=self.admin,
            status=Sprint.Status.CLOSED
        )

        self.client.force_authenticate(
            self.employee
        )

        response = self.client.get(
            self.list_url,
            {'status': Sprint.Status.CLOSED}
        )

        self.assertEqual(
            response.data['count'],
            1
        )

    # --- pagination

    def test_list_is_paginated(self):
        self.client.force_authenticate(
            self.employee
        )

        response = self.client.get(
            self.list_url
        )

        self.assertIn(
            'results',
            response.data
        )

        self.assertIn(
            'count',
            response.data
        )