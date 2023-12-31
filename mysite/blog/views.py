from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm
from django.views.generic import (TemplateView, ListView,
                                  DetailView, CreateView,
                                  DeleteView, UpdateView)
from blog.models import Post, Comment
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class AboutView(TemplateView):
    template_name = 'about.html'


class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    

class PostDetailView(DetailView):
    model = Post


class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = '/login/'
    ### what is this name field???
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post


class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post


class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'blog_draft_list.html'

    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')
    

class PostDeleteView(LoginRequiredMixin, DeleteView):
    #### should I add these???
    # login_url = '/login/'
    # redirect_field_name = 'blog/post_list.html'
    model = Post
    success_url = reverse_lazy('post_list')


#######################################
## Functions that require a pk match ##
#######################################


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form': form})

@login_required
def comment_approve(requset, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)