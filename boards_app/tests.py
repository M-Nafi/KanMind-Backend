"""
Test suite for the boards_app.

Covers:
- Board listing: ownership, membership, authentication, and response format.
- Board creation: successful creation, member assignment, owner assignment, and validation errors.
- Board detail retrieval: access control for owners, members, outsiders, and unauthenticated users.
- Board update: title changes, member updates, and permission checks.
- Board deletion: owner-only deletion, member restrictions, and authentication enforcement.
- Board model: string representation and relationship integrity.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from auth_app.models import User
from boards_app.models import Board


class BoardListTests(TestCase):
    """Tests for listing boards, including ownership, membership visibility, authentication, and response format."""
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='owner@test.com',
            email='owner@test.com',
            password='pass123',
            fullname='Board Owner'
        )
        self.other_user = User.objects.create_user(
            username='other@test.com',
            email='other@test.com',
            password='pass123',
            fullname='Other User'
        )
        self.url = reverse('board-list')
    
    def test_list_boards_authenticated(self):
        board1 = Board.objects.create(title='Board 1', owner=self.user)
        board2 = Board.objects.create(title='Board 2', owner=self.user)
        board2.members.add(self.user)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_list_boards_shows_member_boards(self):
        board = Board.objects.create(title='Shared Board', owner=self.other_user)
        board.members.add(self.user)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Shared Board')
    
    def test_list_boards_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_boards_response_format(self):
        board = Board.objects.create(title='Test Board', owner=self.user)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        board_data = response.data[0]
        self.assertIn('id', board_data)
        self.assertIn('title', board_data)
        self.assertIn('owner_id', board_data)
        self.assertIn('member_count', board_data)
        self.assertIn('ticket_count', board_data)
        self.assertIn('tasks_to_do_count', board_data)
        self.assertIn('tasks_high_prio_count', board_data)


class BoardCreateTests(TestCase):
    """Tests for creating boards, including member assignment, owner assignment, and validation errors."""
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='owner@test.com',
            email='owner@test.com',
            password='pass123',
            fullname='Board Owner'
        )
        self.member = User.objects.create_user(
            username='member@test.com',
            email='member@test.com',
            password='pass123',
            fullname='Member User'
        )
        self.url = reverse('board-list')
        self.client.force_authenticate(user=self.user)
    
    def test_create_board_successful(self):
        data = {
            'title': 'New Project',
            'members': [self.member.id]
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Board.objects.count(), 1)
        self.assertEqual(response.data['title'], 'New Project')
        self.assertIn('owner_data', response.data)
    
    def test_create_board_without_members(self):
        data = {'title': 'Solo Project'}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        board = Board.objects.get(id=response.data['id'])
        self.assertEqual(board.members.count(), 0)
    
    def test_create_board_owner_is_set(self):
        data = {'title': 'Test Board'}
        response = self.client.post(self.url, data)
        
        board = Board.objects.get(id=response.data['id'])
        self.assertEqual(board.owner, self.user)
    
    def test_create_board_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {'title': 'Test Board'}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_board_missing_title(self):
        data = {'members': [self.member.id]}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BoardDetailTests(TestCase):
    """Tests for retrieving board details, covering owner access, member access, outsider restrictions, and authentication."""
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username='owner@test.com',
            email='owner@test.com',
            password='pass123',
            fullname='Board Owner'
        )
        self.member = User.objects.create_user(
            username='member@test.com',
            email='member@test.com',
            password='pass123',
            fullname='Member User'
        )
        self.outsider = User.objects.create_user(
            username='outsider@test.com',
            email='outsider@test.com',
            password='pass123',
            fullname='Outsider'
        )
        self.board = Board.objects.create(title='Test Board', owner=self.owner)
        self.board.members.add(self.member)
    
    def test_retrieve_board_as_owner(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Board')
        self.assertIn('owner_id', response.data)
        self.assertIn('members', response.data)
        self.assertIn('tasks', response.data)
    
    def test_retrieve_board_as_member(self):
        self.client.force_authenticate(user=self.member)
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_board_as_outsider(self):
        self.client.force_authenticate(user=self.outsider)
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_board_unauthenticated(self):
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_nonexistent_board(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('board-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BoardUpdateTests(TestCase):
    """Tests for updating boards, including title changes, member updates, and permission enforcement."""
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
        self.new_member = User.objects.create_user(
            username='new@test.com',
            email='new@test.com',
            password='pass123'
        )
        self.board = Board.objects.create(title='Old Title', owner=self.owner)
        self.board.members.add(self.member)
    
    def test_update_board_title(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        data = {'title': 'New Title'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.board.refresh_from_db()
        self.assertEqual(self.board.title, 'New Title')
    
    def test_update_board_members(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        data = {'members': [self.new_member.id]}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.board.refresh_from_db()
        self.assertIn(self.new_member, self.board.members.all())
        self.assertNotIn(self.member, self.board.members.all())
    
    def test_update_board_as_member(self):
        self.client.force_authenticate(user=self.member)
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        data = {'title': 'Changed by Member'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_board_as_outsider(self):
        outsider = User.objects.create_user(
            username='outsider@test.com',
            email='outsider@test.com',
            password='pass123'
        )
        self.client.force_authenticate(user=outsider)
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        data = {'title': 'Hacked'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BoardDeleteTests(TestCase):
    """Tests for deleting boards, ensuring only owners can delete and enforcing authentication/authorization rules."""
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
        self.board = Board.objects.create(title='Test Board', owner=self.owner)
        self.board.members.add(self.member)
    
    def test_delete_board_as_owner(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Board.objects.count(), 0)
    
    def test_delete_board_as_member(self):
        self.client.force_authenticate(user=self.member)
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Board.objects.count(), 1)
    
    def test_delete_board_unauthenticated(self):
        url = reverse('board-detail', kwargs={'pk': self.board.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BoardModelTests(TestCase):
    """Tests for the Board model, including string representation and relationship integrity with users."""
    def test_board_str(self):
        user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com'
        )
        board = Board.objects.create(title='My Board', owner=user)
        self.assertEqual(str(board), 'My Board')
    
    def test_board_relationships(self):
        owner = User.objects.create_user(
            username='owner@test.com',
            email='owner@test.com'
        )
        member = User.objects.create_user(
            username='member@test.com',
            email='member@test.com'
        )
        board = Board.objects.create(title='Test', owner=owner)
        board.members.add(member)
        
        self.assertEqual(board.owner, owner)
        self.assertIn(member, board.members.all())
        self.assertIn(board, owner.owned_boards.all())
        self.assertIn(board, member.member_boards.all())