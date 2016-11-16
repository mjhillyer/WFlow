from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import discussion.views as views

urlpatterns = [
    url(r'^_discussion_comment_create', views.submit_discussion_comment, name="discussion-comment-create"),
    url(r'^_discussion_comment_edit', views.edit_discussion_comment, name="discussion-comment-edit"),
    url(r'^_discussion_comment_delete', views.delete_discussion_comment, name="discussion-comment-delete"),
    url(r'^_discussion_comment_react', views.save_reaction, name="discussion-comment-react"),
    url(r'^_discussion_poll', views.poll_for_events, name="discussion_poll_for_events"),
]

