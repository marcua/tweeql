from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from mysite.polls.models import Choice, Poll
import datetime


def index(request):
    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    return render_to_response('polls/index.html', {'latest_poll_list': latest_poll_list})
    
def detail(request, poll_id):
        p = get_object_or_404(Poll, pk=poll_id)
        return render_to_response('polls/detail.html', {'poll': p},
                                   context_instance=RequestContext(request))

def results(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    return render_to_response('polls/results.html', {'poll': p})

def vote(request, poll_id):
        p = get_object_or_404(Poll, pk=poll_id)
        try:
            selected_choice = p.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the poll voting form.
            return render_to_response('polls/detail.html', {
                'poll': p,
                'error_message': "You didn't select a choice.",
            }, context_instance=RequestContext(request))
        else:
            selected_choice.votes += 1
            selected_choice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('mysite.polls.views.results', args=(p.id,)))

def add(request):
    return render_to_response('polls/add.html',context_instance=RequestContext(request))
    
def addpole(request):
    p = Poll(question=request.POST['text'], pub_date=datetime.datetime.now())
    p.save()
    return HttpResponseRedirect(reverse('mysite.polls.views.index'))
 
def editpole(request,poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    p.choice_set.create(choice=request.POST['text1'], votes=0)
    p.save()
    return HttpResponseRedirect(reverse('mysite.polls.views.detail',args=(p.id,)))
    
def editpole1(request,poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    p.question=request.POST['text2']
    p.save()
    return HttpResponseRedirect(reverse('mysite.polls.views.index'))

def edit(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    return render_to_response('polls/edit.html', {'poll': p},context_instance=RequestContext(request))
    