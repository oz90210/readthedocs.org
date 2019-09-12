from .mixins import APIEndpointMixin
from django.urls import reverse
import django_dynamic_fixture as fixture

from readthedocs.projects.models import Project


class SubprojectsEndpointTests(APIEndpointMixin):

    def test_projects_subprojects_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(
            reverse(
                'projects-subprojects-list',
                kwargs={
                    'parent_lookup_parent__slug': self.project.slug,
                },
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            self._get_response_dict('projects-subprojects-list'),
        )

    def test_projects_subprojects_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(
            reverse(
                'projects-subprojects-detail',
                kwargs={
                    'parent_lookup_parent__slug': self.project.slug,
                    'alias_slug': self.project_relationship.alias,
                }),
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            self._get_response_dict('projects-subprojects-detail'),
        )

    def test_projects_subprojects_list_post(self):
        newproject = fixture.get(
            Project,
            pub_date=self.created,
            modified_date=self.modified,
            description='Project description',
            repo='https://github.com/rtfd/project',
            project_url='http://project.com',
            name='new-project',
            slug='new-project',
            related_projects=[],
            main_language_project=None,
            users=[self.me],
            versions=[],
        )

        self.assertEqual(self.project.subprojects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        data = {
            'child': newproject.slug,
            'alias': 'subproject-alias',
        }
        response = self.client.post(
            reverse(
                'projects-subprojects-list',
                kwargs={
                    'parent_lookup_parent__slug': self.project.slug,
                },
            ),
            data,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.project.subprojects.count(), 2)

        self.assertDictEqual(
            response.json(),
            self._get_response_dict('projects-subprojects-list_POST'),
        )

    def test_projects_subprojects_list_post_with_others_as_child(self):
        self.assertEqual(self.project.subprojects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        data = {
            'child': self.others_project.slug,
            'alias': 'subproject-alias',
        }
        response = self.client.post(
            reverse(
                'projects-subprojects-list',
                kwargs={
                    'parent_lookup_parent__slug': self.project.slug,
                },
            ),
            data,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.project.subprojects.count(), 1)

    def test_projects_subprojects_list_post_with_others_as_parent(self):
        self.assertEqual(self.others_project.subprojects.count(), 0)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        data = {
            'child': self.project.slug,
            'alias': 'subproject-alias',
        }
        response = self.client.post(
            reverse(
                'projects-subprojects-list',
                kwargs={
                    'parent_lookup_parent__slug': self.others_project.slug,
                },
            ),
            data,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.others_project.subprojects.count(), 0)

    def test_projects_subprojects_detail_delete(self):
        self.assertEqual(self.project.subprojects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.delete(
            reverse(
                'projects-subprojects-detail',
                kwargs={
                    'parent_lookup_parent__slug': self.project.slug,
                    'alias_slug': self.project_relationship.alias,
                },
            ),
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.project.subprojects.count(), 0)

    def test_projects_subprojects_detail_delete_others_project(self):
        newproject = fixture.get(
            Project,
            pub_date=self.created,
            modified_date=self.modified,
            description='Project description',
            repo='https://github.com/rtfd/project',
            project_url='http://project.com',
            name='new-project',
            slug='new-project',
            related_projects=[],
            main_language_project=None,
            users=[self.me],
            versions=[],
        )
        project_relationship = self.others_project.add_subproject(newproject)
        self.assertEqual(self.others_project.subprojects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.delete(
            reverse(
                'projects-subprojects-detail',
                kwargs={
                    'parent_lookup_parent__slug': self.others_project.slug,
                    'alias_slug': project_relationship.alias,
                },
            ),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.project.subprojects.count(), 1)