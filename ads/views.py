from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.urls import reverse_lazy, reverse
from .forms import CreateForm, CommentForm
from .models import Ad, Comment, Fav
from .owner import OwnerListView, OwnerDetailView, OwnerDeleteView
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView

# Create your views here.

class AdListView(OwnerListView):
    model = Ad
    template_name = 'ads/ad_list.html'

    def get(self, request):
        strval = request.GET.get('search', False)
        page = request.GET.get('page')
        if strval:
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            query.add(Q(tags__name__icontains=strval), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().distinct().order_by('-updated_at')[:10]
            try:
                paginator = Paginator(ad_list, 5)
                ads = paginator.page(page)
            except PageNotAnInteger:
                ads = paginator.page(1)
            except EmptyPage:
                ads = paginator.page(paginator.num_pages)
        else:
            ad_list = Ad.objects.all().order_by('-created_at')
            try:
                paginator = Paginator(ad_list, 5)
                ads = paginator.page(page)
            except PageNotAnInteger:
                ads = paginator.page(1)
            except EmptyPage:
                ads = paginator.page(paginator.num_pages)        
        for obj in ad_list:
            obj.natural_updated = naturaltime(obj.updated_at)
        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_ads.values('id')
            favorites = [ row['id'] for row in rows]
        context = { 'ad_list' : ads, 'favorites': favorites, 'search' : strval}
        return render(request, self.template_name , context)

# class AdTagListView(OwnerListView):
#     model = Ad
#     template_name = 'ads/ad_tag_list.html'
    
#     def get(self, request, tag):
#         tags = Tag.objects.filter()

class Tag(OwnerListView):
    model=Ad
    template_name = 'ads/ad_tag_list.html'

    def get(self, request, tag):
        ads = Ad.objects.filter(tags__name=tag)
        if request.user.is_authenticated:
            rows = request.user.favorite_ads.values('id')
            favorites = [ row['id'] for row in rows]
            return render(request, self.template_name , {'ad_list':ads, 'favorites':favorites, 'request':request})
        return render(request, self.template_name , {'ad_list':ads, 'request': request})
 

class AdDetailView(OwnerDetailView):
    model = Ad
    fields = ['title', 'text', 'price', 'tags']
    template_name = 'ads/ad_detail.html'
    def get(self, request, pk) :
        x = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'ad' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)

class Favorites(LoginRequiredMixin, OwnerListView):
    model = Ad
    template_name = 'ads/favorites.html'
    def get(self, request):
        strval = request.GET.get('search', False)
        page = request.GET.get('page')
        favs = Fav.objects.filter(user = request.user)
        fav_ads = []
        for x in favs:
            fav_ads.append(x.ad)
        all_fav_ads = []
        if strval:
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            query.add(Q(tags__name__icontains=strval), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
            all_fav_ads = list(set(fav_ads).intersection(ad_list))
            try:
                paginator = Paginator(all_fav_ads, 5)
                ads = paginator.page(page)
            except PageNotAnInteger:
                ads = paginator.page(1)
            except EmptyPage:
                ads = paginator.page(paginator.num_pages)
        else:
            try:
                paginator = Paginator(fav_ads, 5)
                ads = paginator.page(page)
            except PageNotAnInteger:
                ads = paginator.page(1)
            except EmptyPage:
                ads = paginator.page(paginator.num_pages)        
        for obj in all_fav_ads:
            obj.natural_updated = naturaltime(obj.updated_at)
        favorites = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_ads.values('id')
            favorites = [ row['id'] for row in rows]
        context = { 'ad_list' : ads, 'favorites': favorites, 'search' : strval}
        return render(request, self.template_name , context)



class AdDeleteView(OwnerDeleteView):
    model = Ad

class AdCreateView(LoginRequiredMixin, View):
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:list')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        form.save_m2m()
        return redirect(self.success_url)


class AdUpdateView(LoginRequiredMixin, View):
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:list')

    def get(self, request, pk):
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        pic = form.save(commit=False)
        pic.save()
        form.save_m2m()

        return redirect(self.success_url)

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse('ads:detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:detail', args=[ad.id])



def stream_file(request, pk):
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Add pk", pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Delete pk", pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Ad.DoesNotExist as e:
            pass
        return HttpResponse()


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'