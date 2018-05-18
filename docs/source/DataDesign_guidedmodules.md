Compliance Apps, Modules, Questions, Tasks, and Answers
=======================================================

The diagram below provides a summary representation of GovReady-Q's Django `guidedmodules` data model which handles compliance apps, modules, questions, tasks, and answers.

![Guildedmodules data model (not all tables represented)](assets/govready-q-guidedmodules-erd.png)

The best way to understand the guidedmodules data model is to think of a questionnaire containing multiple questions. Questions can be grouped into modules. Questions come in different types. Questions have answers.

This description suggests a simple "questionnaire-module-question-answer" database model, yet the diagram does not have tables for "Questionnaire" or "Question" or "Answer".

That's because we have a few special demands for our questionnaire that will require creative abstractions. Some of these additional demands are:

* blank questionaires are reusable and can be easily loaded into different installs of the database at different organizations;
* anyone can author questionnaires and blank questionnaires can be kept private or shared publicly;
* one questionnaire's answers can be accessed and used by another questionnaire if the questionnaires are part of the same project;
* arbitrary questionnaires can be associated with the same project; so we won't know up front which answers can be shared;
* support a question type whose answer is another questionnaire;
* allow blank questionnaires to be versioned, answered questionnaires to be updated in non-destructive ways, and to preserve answered questionnaires over the course of years,
* allow the answer to questions to change while preserving a complete history of answers,
* support assigning questionnaires and questions to different users to answer.

The first abstraction is to think of the "questionnaire" as more of a mini-application, or "app", that can could be extended to do more things than just ask questions and track answers. Apps are clearly reusable and easily loaded into different installs of the database and anyone can author them. When we install an app we have an instance of that app. Hence the `AppInstance` table. To enable our install of GovReady-Q to load both public and private apps, we track multiple sources of apps in the `AppSource` table.

The second abstraction is to think of a "question" also as a kind of "task" whose undertaking results in a value to be stored. When we assign a question (or a module of multiple questions) to a user, we task that user to produce a value that answers the question. Hence the tables `Task` and `TaskAnwser`. The `TaskAnswerHistory` table enables us to preserve a history of responses to a taskanswer. The field `stored_value` in the `TaskAnswerHistory` contains the actual response value to the task (e.g., the question's answer).

The simple "questionnaire-module-question-answer" model has now been transformed into a more abstract "app-module-task-taskanswer" model. 

To this "app-module-task-taskanswer" model we add relationships to deal with tasks whose taskanswer are other modules. And we add the `ModuleAssetPack` and `ModuleAsset` tables to track images and other assets our various modules of tasks might need.

This might all seem a long way from compliance, but it's not. Compliance is the discipline of scaling attestation and verification. To show compliance entities attest to completing multiple tasks in a manner that can be verified. Hence, "app-module-task-taskanswer".
