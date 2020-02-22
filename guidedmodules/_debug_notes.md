Major Culprits of slow performance:

1. guidedmodules.Models.Task.is_finished() when a question answere updated
2. evaluate_module_state - when called. Josh said this is an older module
3. SQL query tracking in Django Debug Toolbar



The major culprit of the performance issue is the guidedmodules.Models.Task.is_finished() method

# TODO: Create a better, cached test for is_finished
# `is_finished` should return a value very quickly.
# Until a faster `is_finished` function, assume response is false.
# task_answered = questions[mq.id]['task'].is_finished()


Improve performance: Set `is_finished` to false in progress history

To dramatically improve performance, set `is_finished` check to False when showing question or showing module review page. Current `is_finished` exhibited poor performance causing caches to be rebuilt when answers changed on existing questions. We were checking `is_finished` when building the `task-progress-history-list`.

We need a better `is_finished` test to answer state quickly.

Only lost on user interface is not seeing a check mark for an entire
module in the `task-progress-history-list`.

Also, apply the fix of identify current_group in `task-progress-history-list`
when id and module-id differ to the module review page view, too.




Improve performance: Set `is_finished` to false in progress history
    
    To dramatically improve performance, set `is_finished` check to False
    when showing question or showing module review page.
    
    Current `is_finished` exhibited poor performance causing
    caches to be rebuilt when answers changed on existing questions.
    We were checking `is_finished` when building the `task-progress-history-list`.

```python
   def is_finished(self):
        def compute_is_finished():
            # Check that all questions that need an answer have
            # an answer and that all module-type questions are
            # finished.
```


- in guidedmodules.views:
    `task_answered = questions[mq.id]['task'].is_finished()` really slows down generation of a page after question updated.
    Setting `task_answered` to false instead of running `is_finished` dramatically speeds up page load after change.

L656 or so -- (NOTE this occurs elsewhere)
```python
        if 'task' in questions[mq.id]:
            print("\nquestions[mq.id]['task'].id", questions[mq.id]['task'].id, questions[mq.id]['task'])
            task_link = "/tasks/{}/{}".format(questions[mq.id]['task'].id, "start")
            task_id = questions[mq.id]['task'].id
            task_started = questions[mq.id]['task'].is_started()
            # task_answered = questions[mq.id]['task'].is_finished()
            task_answered = False # Debug
```



FIRST LOAD after changed answer, new question - 820 queries; 17 seconds

```python
SELECT "guidedmodules_module"."id", 
       "guidedmodules_module"."source_id", 
       "guidedmodules_module"."app_id", 
       "guidedmodules_module"."module_name", 
       "guidedmodules_module"."superseded_by_id", 
       "guidedmodules_module"."spec", 
       "guidedmodules_module"."created", 
       "guidedmodules_module"."updated" 
  FROM "guidedmodules_module" 
 WHERE "guidedmodules_module"."id" = '25'
  660 similar queries.   Duplicated 214 times.  


/codedata/code/govready-q-0.9.0-module-nav/venv/lib/python3.7/site-packages/django/contrib/staticfiles/handlers.py in __call__(65)
  return self.application(environ, start_response)
/codedata/code/govready-q-0.9.0-module-nav/siteapp/wsgi.py in application(26)
  return django_application(environ, start_response)
/codedata/code/govready-q-0.9.0-module-nav/venv/lib/python3.7/site-packages/whitenoise/middleware.py in __call__(52)
  response = self.get_response(request)
/codedata/code/govready-q-0.9.0-module-nav/siteapp/middleware.py in __call__(25)
  response = self.next_middleware(request)
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/middleware.py in __call__(16)
  response = self.next_middleware(request)
/codedata/code/govready-q-0.9.0-module-nav/venv/lib/python3.7/site-packages/django/contrib/auth/decorators.py in _wrapped_view(21)
  return view_func(request, *args, **kwargs)
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/views.py in new_view_func(170)
  return view_func(request, task, answered, context, question, *args)
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/views.py in show_question(653)
  task_answered = questions[mq.id]['task'].is_finished()
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in is_finished(773)
  return self._get_cached_state("is_finished", compute_is_finished)
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in _get_cached_state(739)
  self.cached_state[key] = refresh_func()
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in compute_is_finished(754)
  answers = self.get_answers().with_extended_info()
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in get_answers(708)
  for q, a in self.get_current_answer_records():
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in get_current_answer_records(701)
  Task.get_all_current_answer_records([self]):
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in get_all_current_answer_records(686)
  if question.module != task.module: continue


/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/views.py in new_view_func(170)
  return view_func(request, task, answered, context, question, *args)
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/views.py in show_question(570)
  root_task_answers = task.project.root_task.get_answers().with_extended_info()
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in get_answers(708)
  for q, a in self.get_current_answer_records():
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in get_current_answer_records(701)
  Task.get_all_current_answer_records([self]):
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in get_all_current_answer_records(686)
  if question.module != task.module: continue

```

SECOND LOAD, same question - 4.6 seconds
221 Queries

```python
SELECT "guidedmodules_module"."id", 
       "guidedmodules_module"."source_id", 
       "guidedmodules_module"."app_id", 
       "guidedmodules_module"."module_name", 
       "guidedmodules_module"."superseded_by_id", 
       "guidedmodules_module"."spec", 
       "guidedmodules_module"."created", 
       "guidedmodules_module"."updated" 
  FROM "guidedmodules_module" 
 WHERE "guidedmodules_module"."id" = '25'
  92 similar queries.   Duplicated 55 times.


/codedata/code/govready-q-0.9.0-module-nav/venv/lib/python3.7/site-packages/django/contrib/staticfiles/handlers.py in __call__(65)
  return self.application(environ, start_response)
/codedata/code/govready-q-0.9.0-module-nav/siteapp/wsgi.py in application(26)
  return django_application(environ, start_response)
/codedata/code/govready-q-0.9.0-module-nav/venv/lib/python3.7/site-packages/whitenoise/middleware.py in __call__(52)
  response = self.get_response(request)
/codedata/code/govready-q-0.9.0-module-nav/siteapp/middleware.py in __call__(25)
  response = self.next_middleware(request)
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/middleware.py in __call__(16)
  response = self.next_middleware(request)
/codedata/code/govready-q-0.9.0-module-nav/venv/lib/python3.7/site-packages/django/contrib/auth/decorators.py in _wrapped_view(21)
  return view_func(request, *args, **kwargs)
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/views.py in new_view_func(151)
  answered = task.get_answers().with_extended_info()
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in get_answers(708)
  for q, a in self.get_current_answer_records():
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in get_current_answer_records(701)
  Task.get_all_current_answer_records([self]):
/codedata/code/govready-q-0.9.0-module-nav/guidedmodules/models.py in get_all_current_answer_records(686)
  if question.module != task.module: continue
```
