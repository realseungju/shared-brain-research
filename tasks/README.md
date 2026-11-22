# Tasks

```text
backlog/ → doing/ → done/
```

Work with a done condition — running research, implementing, validating — lives here. Questions
and results go in `research/`, meeting sources in `feedback/`, and a task links to those paths.

The AI creates a new task with the generator.

```sh
python infra/new-task.py {slug} --title "Title"
```

After creation, fill in the success criteria and the related experiment and feedback paths. When
moving it to `doing/`, record `agent` and `started`; when closing it into `done/`, record
`finished`, `closed_reason`, and the real `result`.
