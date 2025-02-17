import random
import json
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.views.generic import CreateView
from django.views.generic.list import ListView
from django.db.models import Avg
from django.core.mail import send_mail

from tour.forms import *
from .models import *



class TourListView(ListView):
    model = Tour
    context_object_name = 'tours'
    template_name = "tour-list.html"
    paginate_by = 16

    def get_queryset(self):
        if self.request.method == 'GET':
            queryset1 = Tour.objects.filter(status=1)
            title_name = self.request.GET.get('q', None)
            if title_name is not None:
                queryset = queryset1.filter(title__icontains=title_name, status=1)
                return queryset

            price_query = self.request.GET.get('price')
            if price_query:
                if price_query == 'high':
                    queryset = Tour.objects.filter(status=1).order_by('-price')
                elif price_query == 'low':
                    queryset = Tour.objects.filter(status=1).order_by('price')
                return queryset

            rating_query = self.request.GET.get('rating')
            if rating_query:
                if rating_query == 'high':
                    queryset = Tour.objects.filter(status=1).order_by('rating')
                    print(queryset)
                elif rating_query == 'low':
                    queryset = Tour.objects.filter(status=1).order_by('-rating')
                return queryset

            duration_query = self.request.GET.get('duration')
            if duration_query:
                if duration_query == 'long':
                    # context2['duration2'] = 'long'
                    queryset = Tour.objects.filter(status=1).order_by('-durationday')
                elif duration_query == 'short':
                    queryset = Tour.objects.filter(status=1).order_by('durationday')
                return queryset

            country_query = self.request.GET.get('country')
            if country_query:
                queryset = Tour.objects.filter(country__icontains=country_query, status=1)
                return queryset

            style_query = self.request.GET.get('style')
            if style_query:
                queryset = Tour.objects.filter(tour_type=TourType.objects.filter(title=style_query).first().id,status=1)
                return queryset

            discount_query = self.request.GET.get('discount')
            if discount_query:
                queryset = Tour.objects.filter(discount__gte=1, status=1)
                return queryset

        return super().get_queryset().filter(status=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour_types = TourType.objects.all()
        tour_type_list = []

        if tour_types:
            for tour_type in tour_types:
                if tour_type.title not in tour_type_list:
                    tour_type_list.append(tour_type.title)

        tours = Tour.objects.all()
        tour_country_list = []
        if tours:
            for tour in tours:
                if tour.country not in tour_country_list:
                    tour_country_list.append(tour.country)

        context["countries"] = tour_country_list
        context['tour_types'] = tour_type_list
        return context


def TourList(request):
    data = Tour.objects.all()
    country = []
    for i in data:
        if i.country not in country:
            country.append(i.country)
    data = Tour.objects.filter(status=1)
    paginator = Paginator(data, 30)
    page_request = 'page'
    page = request.GET.get(page_request)
    try:
        eachpage = paginator.page(page)
    except PageNotAnInteger:
        eachpage = paginator.page(1)
    except EmptyPage:
        eachpage = paginator.page(paginator.num_pages)

    arr = []
    for i in range(0, eachpage.paginator.num_pages):
        arr.append(i+1)

    context = {
        'tour': eachpage,
        'page': page_request,
        'paginator': arr,
        'country': country,
        'style': style,
        'link': request.build_absolute_uri(),
        'model': 'tour'
    }
    return render(request, 'tour-list.html', context)


def TourDetailView(request, pk):
    tour = Tour.objects.get(pk=pk)
    image = TourImage.objects.filter(tour=tour)
    schedule = TourSchedule.objects.filter(tour=tour)
    url = TourUrl.objects.filter(tour=tour)

    # description = {
    #     'tour_detail' : TourDetail.objects.filter(tour=tour),
    #     'description_az' : tour.description_az,
    #     'description_ru' : tour.description_ru,
    #     'description_en' : tour.description_en
    # }


    if request.method == 'POST':
        form = TourCommentForm(request.POST)
        if request.POST.get('form_id') == 'myform':
            textarea = request.POST.get('textarea')
            rating = request.POST.get('rating')
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            if parent_id:
                    parent_obj = TourComment.objects.get(id=parent_id)
                    # replay_comment = form.save(commit=False)
                    # assign parent_obj to replay comment
                    # replay_comment.comment_reply = parent_obj
            comment = TourComment.objects.create(
                message = textarea,
                rating = rating if rating else 0,
                tour = Tour.objects.get(pk=pk),
                user = request.user
            )

            response_data = {

            }

            return HttpResponse(
                    json.dumps(response_data, indent=4, sort_keys=True, default=str),
                    content_type="application/json"
                )

        elif request.POST.get('form_id') == 'p-2 reply-form':
            textarea = request.POST.get('textarea')
            rating = request.POST.get('rating')
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            if parent_id:
                parent_obj = TourComment.objects.get(id=parent_id)
                comment = TourComment.objects.create(
                    message = textarea,
                    rating = rating,
                    tour = Tour.objects.get(pk=pk),
                    user = request.user,
                    comment_reply = parent_obj

                )
            else:
                comment = TourComment.objects.create(
                    message = textarea,
                    rating = rating,
                    tour = Tour.objects.get(pk=pk),
                    user = request.user,
                )

            response_data = {

            }
            response_data['comments'] = TourComment.objects.filter(tour = tour)
            return HttpResponse(
                    json.dumps(response_data, indent=4, sort_keys=True, default=str),
                    content_type="application/json"
                )

        else:
            return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )
    else:
        form = TourCommentForm()

    top_tours = sorted(Tour.objects.filter(status=1).order_by('rating')[:5], key=lambda x: random.random())

    context = {
        'top_tours': top_tours,
        'tour': tour,
        'image': image,
        'schedule': schedule,
        'url': url,
        # 'description': description,
        'form' : form,
        'comments' : tour.tour_comment.filter(comment_reply__isnull=True),
        'comments_count': tour.tour_comment.all()

    }
    tour_view = 'tour_'
    tour_view += str(pk)
    tour_view += '_viewed'

    if tour.tour_comment.all():
        total_tour_comment = int(tour.tour_comment.aggregate(Avg('rating')).get('rating__avg', 0))
        tour.rating = total_tour_comment
        tour.save()


    if not request.COOKIES.get(tour_view):
        response = render(request, 'tour-page.html', context)
        response.set_cookie(tour_view, 'true', max_age=604800)
        tour.viewcount += 1
        tour.save()
        context['tour'] = tour
        return response
    return render(request, 'tour-page.html', context)


def update_items(request, pk):
    tour = Tour.objects.get(pk=pk)

    if request.method == 'POST':
        form = TourCommentForm(request.POST)

        if request.POST.get('form_id') == 'p-2 reply-form':
            textarea = request.POST.get('textarea')
            rating = request.POST.get('rating')
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            if parent_id:
                parent_obj = TourComment.objects.get(id=parent_id)

                comment = TourComment.objects.create(
                    message = textarea,
                    rating = rating,
                    tour = Tour.objects.get(pk=pk),
                    user = request.user,
                    comment_reply = parent_obj

                )
            else:
                comment = TourComment.objects.create(
                    message = textarea,
                    rating = rating,
                    tour = Tour.objects.get(pk=pk),
                    user = request.user,
                )

            response_data = {

            }
            response_data['comments'] = TourComment.objects.filter(tour = tour)
            return HttpResponse(
                    json.dumps(response_data, indent=4, sort_keys=True, default=str),
                    content_type="application/json"
                )

        else:
            return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )
    else:
        form = TourCommentForm()

    context = {
        'form' : form,
        'tour' : tour,
        'comments' : tour.tour_comment.filter(comment_reply__isnull=True),
        'comments_count': tour.tour_comment.all()

    }
    return render(request, 'partials/tour-comments.html', context)


def TourFilter(request):
    print('okkkk')

    context2 = {}
    data = Tour.objects.all()
    price_query = request.GET.get('price')
    if price_query:
        if price_query == 'high':
            context2['price2'] = 'high'
            data = Tour.objects.filter(status=1).order_by('-price')
        elif price_query == 'low':
            context2['price2'] = 'low'
            data = Tour.objects.filter(status=1).order_by('price')
    rating_query = request.GET.get('rating')
    if rating_query:
        if rating_query == 'high':
            context2['rating2'] = 'high'
            data = Tour.objects.filter(status=1).order_by('-rating')
        elif rating_query == 'low':
            context2['rating2'] = 'low'
            data = Tour.objects.filter(status=1).order_by('rating')
    duration_query = request.GET.get('duration')
    if duration_query:
        if duration_query == 'long':
            context2['duration2'] = 'long'
            data = Tour.objects.filter(status=1).order_by('-durationday')
        elif duration_query == 'short':
            context2['duration2'] = 'short'
            data = Tour.objects.filter(status=1).order_by('durationday')

    country_query = request.GET.get('country')
    if country_query:
        context2['country2'] = country_query
        data = Tour.objects.filter(country__icontains=country_query, status=1)

    # discount_query = request.GET.get('discount')
    # if discount_query:
    #     context2['discount2'] = '1'
    #     data = Tour.objects.filter(discount__isnull=False)

    style_query = request.GET.get('style')
    if style_query:
        context2['style2'] = style_query
        data = Tour.objects.filter(tour_type=TourType.objects.filter(title=style_query).first().id, status=1)


    # if request.GET.get('search'):
    #     context2['search2'] = request.GET.get('search')
    #     data = Tour.objects.filter(keyword__icontains=request.GET.get('search'))

    # paginator = Paginator(data, 2)
    # page_request = 'page'
    # page = request.GET.get(page_request)
    # try:
    #     eachpage = paginator.page(page)
    # except PageNotAnInteger:
    #     eachpage = paginator.page(1)
    # except EmptyPage:
    #     eachpage = paginator.page(paginator.num_pages)

    # arr = []
    # for i in range(0, eachpage.paginator.num_pages):
    #     arr.append(i+1)
    # haslink = True

    context = {
        'tours': data,
        'tour_types' : tour_type_list,
        # 'page': page_request,
        # 'paginator': arr,
        'countries': tour_country_list,
        # 'link': request.build_absolute_uri(),
        # 'style': style,
        # 'haslink': haslink
    }
    print(context)
    if context2:
        context.update(context2)
        context.update({'query': 1})
    if len(data) == 0:
        context.update( {'notfound': 'No result found'} )
    return render(request, 'tour-list.html', context)


class TourDenyView(CreateView):
    model = TourDeny
    form_class = TourDenyForm
    template_name = 'deny-message.html'

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        tour = Tour.objects.filter(pk = self.kwargs['pk']).first()
        context['object'] = tour
        return context

    def form_valid(self, form):
        tour = Tour.objects.filter(pk = self.kwargs['pk']).first()
        deny_tour = form.save(commit=False)
        deny_tour.tour = tour
        deny_tour.save()
        send_mail(
            'Subject here',
            deny_tour.message,
            'sara.axmedova98@gmail.com',
            [tour.organizer.user.email],
            fail_silently=False,
        )

        return redirect('main:home')