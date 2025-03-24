from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from  .models import Post
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import PermissionRequiredMixin

class NewsList(ListView):
    model = Post
    ordering = '-timestamp'
    template_name = 'news_list.html'
    context_object_name = 'news'
    paginate_by = 10


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lenght'] = len(Post.objects.all())
        return context

class NewsDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'news_detail'

class NewsSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'news_search'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter_set = PostFilter(self.request.GET, queryset=queryset)
        return self.filter_set.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_set'] = self.filter_set
        return context

class PostCreateMixin(PermissionRequiredMixin, CreateView):
    permission_required = ('news_portal_dev.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        if 'news/create' in self.request.path:
            form.instance.post_type = 'news'
        elif 'articles/create' in self.request.path:
            form.instance.post_type = 'article'
        return super().form_valid(form)

class NewsCreate(PostCreateMixin):
    pass


#пример кода на будущее
#class NewsCreate(CreateView):
#    form_class = PostForm
#    model = Post
#    template_name = 'news_edit.html'


class PostUpdateMixin(PermissionRequiredMixin,UpdateView):
    permission_required = ('news_portal_dev.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        if 'news/create' in self.request.path:
            form.instance.post_type = 'news'
        elif 'articles/create' in self.request.path:
            form.instance.post_type = 'article'
        return super().form_valid(form)

class NewsUpdate(PostUpdateMixin):
    pass


class PostDeleteMixin(PermissionRequiredMixin, DeleteView):
    permission_required = ('news_portal_dev.delete_post',)
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.post_type == 'news':
            self.success_url = reverse_lazy('news_list')
        elif self.object.post_type == 'article':
            self.success_url = reverse_lazy('news_list')
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

class NewsDelete(PostDeleteMixin):
    pass

