from django.db.models import Sum

from blog.models import Blog, Article, Comment, VisitByDate

import datetime


def add_visit_number(request, obj):
    # calculate visit counts
    try:
        visit_by_date = obj.visitbydate.get(date=datetime.date.today())
    except VisitByDate.DoesNotExist:
        visit_by_date = None
    try:
        user = obj.user
    except:  # article does not have user attr.
        user = obj.blog.user
    dict_name = 'visit_' + obj.__class__.__name__
    if request.user != user:
        visited = request.session.get(dict_name, None)
        # print(dict_name, visited)
        if not visited or str(obj.pk) not in visited:  # haven't visit any blog or haven't visit this blog
            if not visited:
                request.session[dict_name] = {obj.pk: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            else:
                visited[str(obj.pk)] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if visit_by_date:  # whether this blog haven't been visited today or not
                visit_by_date.num_visit += 1
            else:
                obj.visitbydate.create(num_visit=1, date=datetime.date.today())
                visit_by_date = obj.visitbydate.get(date=datetime.date.today())
            obj.total_visit += 1
    
        else:
            dt = datetime.datetime.now() - datetime.datetime.strptime(visited[str(obj.pk)], "%Y-%m-%d %H:%M:%S")
            if dt.total_seconds() > 3600:  # larger than 1 hour
                visited[str(obj.pk)] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if visit_by_date:  # whether this obj has been visited today or not
                    visit_by_date.num_visit += 1
                else:
                    obj.visitbydate.create(num_visit=1, date=datetime.date.today())
                    visit_by_date = obj.visitbydate.get(date=datetime.date.today())
                obj.total_visit += 1
        request.session.modified = True
        if visit_by_date:
            visit_by_date.save()
        obj.save()
    return visit_by_date


def n_day_hot(n, model):
    n_day_before = datetime.date.today() - datetime.timedelta(days=n)
    q = model.objects.filter(visitbydate__date__gte=n_day_before).annotate(n_day_visit=Sum('visitbydate__num_visit')).order_by('-n_day_visit')
    if q.count() == 0:
        q = model.objects.order_by('total_visit')
    return q
