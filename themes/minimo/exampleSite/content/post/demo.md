---
date: 2017-09-30T00:00:00+06:00
title: Demo
---

I'm talking about the `bar` function.

* And here I'm talking in a list
 * about `baz`

```java
package mypackage.controller;

import mypackage.Employee;
import mypackage.repository.SQLRepository;
import mypackage.renderer.Renderer;

public class Controller {
    private SQLRepository repository;
    private Renderer renderer;

    public Controller() {
        repository = new SQLRepository();
        renderer = new Renderer();
    }

    public String viewEmployee(int id) {
        Employee employee = repository.getEmployeeByID(id);
        String res = renderer.renderEmployee(employee);
        return res;
    }
}
```

```python
def bar():
   return 1 + 2
```

{{< note >}} this is a note {{</ note >}}

{{< audio "it-was-at-this-moment.mp3" >}}

{{< scene
  title="Resurrecting Dinosaurs, what could possibly go wrong?"
  link="https://fosdem.org/2017/schedule/event/dinosaurs/"
>}}
SPEAKER: I did not expect to have a win32 architecture slide here at FOSDEM
{{< /scene >}}

{{< spoiler >}}
Spoiler!
{{</ spoiler >}}
