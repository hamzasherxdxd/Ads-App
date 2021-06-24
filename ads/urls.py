from django.urls import path, reverse_lazy
from .views import AdCreateView, AdDeleteView, AdDetailView, AdListView, AdUpdateView, CommentCreateView, AddFavoriteView, DeleteFavoriteView, CommentDeleteView, Tag, Favorites, SignUpView
from .import views

app_name = 'ads'
urlpatterns = [
    path('', AdListView.as_view(), name='list'),
    path('create/', AdCreateView.as_view(), name='create'),
    path('<int:pk>/update', AdUpdateView.as_view(), name='update'),
    path('<int:pk>/detail', AdDetailView.as_view(), name='detail'),
    path('<int:pk>/delete', AdDeleteView.as_view(), name='delete'),
    path('ad_picture/<int:pk>', views.stream_file, name='ad_picture'),
    path('<int:pk>/comment', CommentCreateView.as_view(), name='ad_comment_create'),
    path('comment/<int:pk>/delete', 
        CommentDeleteView.as_view(success_url=reverse_lazy('ads:list')), name='ad_comment_delete'),
    path('favorites/', Favorites.as_view(), name='favorites'),
    path('<int:pk>/favorite', AddFavoriteView.as_view(), name='favorite'),
    path('<int:pk>/unfavorite', DeleteFavoriteView.as_view(), name='unfavorite'),
    path('<slug:tag>',Tag.as_view(), name='tag_list'),
    path('signup/', SignUpView.as_view(), name='signup'),
]