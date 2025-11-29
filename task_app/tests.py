"""
Test suite for the task_app.

Covers:
- Tasks assigned to me endpoint.
- Tasks reviewing endpoint.
- Task creation (validation, permissions, assignee/reviewer validation).
- Task updates (title, status, board-change prevention).
- Task deletion (creator and board owner permissions).
- Comment listing, creation, and deletion.
- Task and Comment model string representation.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from auth_app.models import User
from boards_app.models import Board
from task_app.models import Task, Comment


class TaskAssignedToMeTests(TestCase):
    """Tests for GET /api/tasks/assigned-to-me/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='user@test.com',
            email='user@test.com',
            password='pass123'
        )
        self.other_user = User.objects.create_user(
            username='other@test.com',
            email='other@test.com',
            password='pass123'
        )
        self.board = Board.objects.create(title='Test Board', owner=self.user)
        self.url = reverse('task-assigned-to-me')

    def test_assigned_to_me_shows_correct_tasks(self):
        """Test that only tasks assigned to current user are returned."""
        task1 = Task.objects.create(
            title='My Task',
            board=self.board,
            assignee=self.user,
            created_by=self.user
        )
        task2 = Task.objects.create(
            title='Other Task',
            board=self.board,
            assignee=self.other_user,
            created_by=self.user
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'My Task')

    def test_assigned_to_me_unauthenticated(self):
        """Test that unauthenticated requests return 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskReviewingTests(TestCase):
    """Tests for GET /api/tasks/reviewing/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='user@test.com',
            email='user@test.com',
            password='pass123'
        )
        self.other_user = User.objects.create_user(
            username='other@test.com',
            email='other@test.com',
            password='pass123'
        )
        self.board = Board.objects.create(title='Test Board', owner=self.user)
        self.url = reverse('task-reviewing')

    def test_reviewing_shows_correct_tasks(self):
        """Test that only tasks being reviewed by current user are returned."""
        task1 = Task.objects.create(
            title='Review Task',
            board=self.board,
            reviewer=self.user,
            created_by=self.user
        )
        task2 = Task.objects.create(
            title='Other Review',
            board=self.board,
            reviewer=self.other_user,
            created_by=self.user
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Review Task')


class TaskCreateTests(TestCase):
    """Tests for POST /api/tasks/ endpoint and validation."""

    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username='owner@test.com',
            email='owner@test.com',
            password='pass123'
        )
        self.member = User.objects.create_user(
            username='member@test.com',
            email='member@test.com',
            password='pass123'
        )
        self.outsider = User.objects.create_user(
            username='outsider@test.com',
            email='outsider@test.com',
            password='pass123'
        )
        self.board = Board.objects.create(title='Test Board', owner=self.owner)
        self.board.members.add(self.member)
        self.url = reverse('task-list')

    def test_create_task_successful(self):
        """Test successful task creation with all fields."""
        self.client.force_authenticate(user=self.owner)
        data = {
            'board': self.board.id,
            'title': 'New Task',
            'description': 'Task description',
            'status': 'to-do',
            'priority': 'high',
            'assignee_id': self.member.id,
            'reviewer_id': self.owner.id,
            'due_date': '2025-12-31'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.title, 'New Task')
        self.assertEqual(task.created_by, self.owner)

    def test_create_task_minimal_data(self):
        """Test task creation with minimal required data."""
        self.client.force_authenticate(user=self.owner)
        data = {
            'board': self.board.id,
            'title': 'Minimal Task'
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task_assignee_not_member(self):
        """Test that assignee must be a board member."""
        self.client.force_authenticate(user=self.owner)
        data = {
            'board': self.board.id,
            'title': 'Task',
            'assignee_id': self.outsider.id
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_reviewer_not_member(self):
        """Test that reviewer must be a board member."""
        self.client.force_authenticate(user=self.owner)
        data = {
            'board': self.board.id,
            'title': 'Task',
            'reviewer_id': self.outsider.id
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_unauthenticated(self):
        """Test that unauthenticated requests return 401."""
        data = {'board': self.board.id, 'title': 'Task'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_missing_title(self):
        """Test that title field is required."""
        self.client.force_authenticate(user=self.owner)
        data = {'board': self.board.id}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TaskUpdateTests(TestCase):
    """Tests for PATCH /api/tasks/{id}/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username='owner@test.com',
            email='owner@test.com',
            password='pass123'
        )
        self.member = User.objects.create_user(
            username='member@test.com',
            email='member@test.com',
            password='pass123'
        )
        self.outsider = User.objects.create_user(
            username='outsider@test.com',
            email='outsider@test.com',
            password='pass123'
        )
        self.board = Board.objects.create(title='Test Board', owner=self.owner)
        self.board.members.add(self.member)
        self.task = Task.objects.create(
            title='Old Title',
            board=self.board,
            status='to-do',
            created_by=self.owner
        )

    def test_update_task_title(self):
        """Test updating task title."""
        self.client.force_authenticate(user=self.owner)
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        data = {'title': 'New Title'}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'New Title')

    def test_update_task_status(self):
        """Test updating task status."""
        self.client.force_authenticate(user=self.owner)
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        data = {'status': 'done'}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'done')

    def test_update_task_cannot_change_board(self):
        """Test that board field cannot be changed after creation."""
        other_board = Board.objects.create(
            title='Other Board',
            owner=self.owner
        )
        self.client.force_authenticate(user=self.owner)
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        data = {'board': other_board.id}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_task_as_member(self):
        """Test that board members can update tasks."""
        self.client.force_authenticate(user=self.member)
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        data = {'title': 'Changed by Member'}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_task_as_outsider(self):
        """Test that non-members cannot update tasks (403 Forbidden)."""
        self.client.force_authenticate(user=self.outsider)
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        data = {'title': 'Hacked'}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TaskDeleteTests(TestCase):
    """Tests for DELETE /api/tasks/{id}/ endpoint and permissions."""

    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username='owner@test.com',
            email='owner@test.com',
            password='pass123'
        )
        self.creator = User.objects.create_user(
            username='creator@test.com',
            email='creator@test.com',
            password='pass123'
        )
        self.member = User.objects.create_user(
            username='member@test.com',
            email='member@test.com',
            password='pass123'
        )
        self.board = Board.objects.create(title='Test Board', owner=self.owner)
        self.board.members.add(self.creator, self.member)
        self.task = Task.objects.create(
            title='Test Task',
            board=self.board,
            created_by=self.creator
        )

    def test_delete_task_as_creator(self):
        """Test that task creator can delete their own task."""
        self.client.force_authenticate(user=self.creator)
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_delete_task_as_board_owner(self):
        """Test that board owner can delete any task on their board."""
        self.client.force_authenticate(user=self.owner)
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_delete_task_as_member(self):
        """Test that regular members cannot delete tasks (403 Forbidden)."""
        self.client.force_authenticate(user=self.member)
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Task.objects.count(), 1)


class CommentListTests(TestCase):
    """Tests for GET /api/tasks/{id}/comments/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='user@test.com',
            email='user@test.com',
            password='pass123',
            fullname='Test User'
        )
        self.board = Board.objects.create(title='Board', owner=self.user)
        self.task = Task.objects.create(
            title='Task',
            board=self.board,
            created_by=self.user
        )

    def test_list_comments(self):
        """Test retrieving all comments for a task."""
        comment1 = Comment.objects.create(
            task=self.task,
            author=self.user,
            text='First comment'
        )
        comment2 = Comment.objects.create(
            task=self.task,
            author=self.user,
            text='Second comment'
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('task-comments-list', kwargs={'task_pk': self.task.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_comments_empty(self):
        """Test retrieving comments when task has none."""
        self.client.force_authenticate(user=self.user)
        url = reverse('task-comments-list', kwargs={'task_pk': self.task.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class CommentCreateTests(TestCase):
    """Tests for POST /api/tasks/{id}/comments/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='user@test.com',
            email='user@test.com',
            password='pass123',
            fullname='Test User'
        )
        self.board = Board.objects.create(title='Board', owner=self.user)
        self.task = Task.objects.create(
            title='Task',
            board=self.board,
            created_by=self.user
        )

    def test_create_comment(self):
        """Test successful comment creation."""
        self.client.force_authenticate(user=self.user)
        url = reverse('task-comments-list', kwargs={'task_pk': self.task.id})
        data = {'content': 'This is a comment'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'This is a comment')
        self.assertEqual(comment.author, self.user)

    def test_create_comment_author_set_automatically(self):
        """Test that comment author is set from authenticated user."""
        self.client.force_authenticate(user=self.user)
        url = reverse('task-comments-list', kwargs={'task_pk': self.task.id})
        data = {'content': 'Test'}
        response = self.client.post(url, data)

        comment = Comment.objects.first()
        self.assertEqual(comment.author, self.user)

    def test_create_comment_missing_content(self):
        """Test that content field is required."""
        self.client.force_authenticate(user=self.user)
        url = reverse('task-comments-list', kwargs={'task_pk': self.task.id})
        data = {}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentDeleteTests(TestCase):
    """Tests for DELETE /api/tasks/{id}/comments/{id}/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.author = User.objects.create_user(
            username='author@test.com',
            email='author@test.com',
            password='pass123'
        )
        self.other_user = User.objects.create_user(
            username='other@test.com',
            email='other@test.com',
            password='pass123'
        )
        self.board = Board.objects.create(title='Board', owner=self.author)
        self.task = Task.objects.create(
            title='Task',
            board=self.board,
            created_by=self.author
        )
        self.comment = Comment.objects.create(
            task=self.task,
            author=self.author,
            text='Test comment'
        )

    def test_delete_comment_as_author(self):
        """Test that comment author can delete their own comment."""
        self.client.force_authenticate(user=self.author)
        url = reverse('task-comments-detail', kwargs={
            'task_pk': self.task.id,
            'pk': self.comment.id
        })
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_as_other_user(self):
        """Test that non-authors cannot delete comments (403 Forbidden)."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('task-comments-detail', kwargs={
            'task_pk': self.task.id,
            'pk': self.comment.id
        })
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 1)


class TaskModelTests(TestCase):
    """Tests for Task model string representation."""

    def test_task_str(self):
        """Test that task __str__ returns the title."""
        user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com'
        )
        board = Board.objects.create(title='Board', owner=user)
        task = Task.objects.create(
            title='Test Task',
            board=board,
            created_by=user
        )
        self.assertEqual(str(task), 'Test Task')


class CommentModelTests(TestCase):
    """Tests for Comment model string representation."""

    def test_comment_str(self):
        """Test that comment __str__ includes author and task info."""
        user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            fullname='Test User'
        )
        board = Board.objects.create(title='Board', owner=user)
        task = Task.objects.create(
            title='Task',
            board=board,
            created_by=user
        )
        comment = Comment.objects.create(
            task=task,
            author=user,
            text='Test'
        )
        self.assertIn('Test User', str(comment))
        self.assertIn('Task', str(comment))
