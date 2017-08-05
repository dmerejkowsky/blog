---
slug: non-isomorphic-cpp-refactoring
date: 2017-08-05T13:48:21.878603+00:00
draft: false
title: Non isomorphic C++ refactoring
tags: ["c++"]
summary: A small example of a innocent-looking C++ refactoring going terribly wrong.
---

# Introduction

Let me tell you a story about a C++  refactoring, based on real events.

The example is a little bit contrived, but the code is actually quite close to
what it really looked like.

Also, note that I'm no C++ expert, so pardon my mistakes.

# The problem

Let's say you are writing a C++ program to safely store important documents.

You have one of these fancy safes that open with a combination and a key.
You have to enter the combination *before* inserting the key , but the safe
automatically locks itself as soon as you close the door. (that may be not
exactly how safes work, but it's convenient for our example).

You already have the `main()` function written, like so:

```cpp
int main() {
  Safe safe;
  Document passport("passport");
  Document idCard("ID card");
  std::list<Document> documents{passport, idCard};

  safelyStoreDocuments(safe, documents);
  return 0;
}
```

Your job is to write the `safelyStoreDocuments` function.

# Using RAII for the door

You just read about RAII (resource acquisition is initialization) pattern so you
decide to use it.

Quick reminder about what RAII is: In C++, the destructor of a class is
guaranteed to be called when the scope where the instance was created is exited.
It can be used to implement a lock, like so:

```cpp
class Lock {
  public:
  Lock() {
    _mutex.acquire();
  }
  ~Lock() {
    _mutex.release();
  }

  private: {
    Mutex _mutex;
  }
}:

void doSomething() {
  {
    Lock lock;
    updateCounter();
  }
};
```

Here you know that the lock will be acquired right before `updateCounter()`  is
called, and then release right after.

So you decide to implement the same pattern for the safe's door:

```cpp
class Door {
  public:
  void close() {
    // ...
  }

  ~Door() {
    close();
  }
};
```
Thus you can start implementing the `safelyStoreDocuments` function:

```cpp
void safelyStoreDocuments(Safe& safe, std::list<Document> const& documents) {
  Door door;

  // TODO: open the door and store documents
}
```

Note how we use a safe *reference*, to make sure no copy of the safe is done,
and to make sure the safe is initialized.

# Remembering the combination

Finding the combination is not difficult, you just
have to think really hard first:


```cpp
void safelyStoreDocuments(Safe& safe, std::list<Document> const& documents) {
  Door door;

  // Find and enter combination:
  Brain brain;
  brain.thinkReallyHard();
  auto combination = brain.getCombination();
  door.enterCombination(combination);

  // TODO: unlock the door
  // TODO: store documents
}
```


# Looking for the key

Find the key is a bit tricky. You have to iterate through all the pockets to
find the one that contains the key.

Once the key is found, all you have to do is to unlock the door
with the key and open it:

Your code now looks like:
```cpp
Pocket findCorrectPocket() {
  for(auto pocket: pockets) {
    // ...
  }
}

void safelyStoreDocuments() {
  Door door;

  // Find and enter combination:
  Brain brain;
  brain.thinkReallyHard();
  auto combination = brain.getCombination();
  door.enterCombination(combination);

  // Find the key and unlock the door
  auto correctPocket = findCorrectPocket();
  auto key = correctPocket.key();
  door.unlock(key);

  door.open();

  // TODO: store documents
}
```

# Storing documents

Storing documents is quite easy: you just have to loop, checking that
there is enough room in the safe.

So you are finally able to implement the TODO:

```cpp
void safelyStoreDocuments() {
  Door door;

  // Find and enter combination:
  Brain brain;
  brain.thinkReallyHard();
  auto combination = brain.getCombination();
  door.enterCombination(combination);

  // Find the key and unlock the door
  auto correctPocket = findCorrectPocket();
  auto key = correctPocket.key();
  door.unlock(key);

  door.open();

  // Put documents in the safe:
  for(auto const& document: documents) {
    safe.checkAvailableRoom();
    safe.putDocument(document);
  }

}
```

Satisfied with your work, you compile and run the code:

```console
$ g++ -Wall safe.cpp -o safe && ./safe
Thinking really hard about combination ...
Entering combination
Looking for correct pocket ...
Unlock door
Opening door
Putting passport in safe
Putting ID card in safe
Closing door
```

Looks like the code is working!

# Cleaning up

Satisfied, you submit your changes for code review.

One of your colleagues points out a code smell. The function is long with
explanatory comments. It would be better to extract some of the functionality
into smaller functions.

You agree, and re-write the code:

```cpp
void openSafeDoor() {
  Door door;
  Brain brain;
  brain.thinkReallyHard();
  auto combination = brain.getCombination();
  door.enterCombination(combination);

  auto correctPocket = findCorrectPocket();
  auto key = correctPocket.key();
  door.unlock(key);

  door.open();
}

void putDocumentsIntoSafe(Safe& safe, std::list<Document> const& documents) {
  for(auto document: documents) {
    safe.checkAvailableRoom();
    safe.putDocument(document);
  }
}

void safelyStoreDocuments(Safe& safe, std::list<Document> const& documents) {
  openSafeDoor();
  putDocumentsIntoSafe(safe, documents);
}
```

Spot the mistake yet?

I'll let you think about it for a few minutes, while enjoying this
animated graphical music score:

{{< youtube O_XKi_DaPsc >}}

# The mistake

When we split the function in two, we moved the instantiation of the Door
class in the `openSafeDoor()` function, which means the door will be _closed_
by the time we try to put the documents in the safe!


# How did it happen

That's a question I always asked myself when I write a patch for a bug fix.

Why did the bug appear, and what can we do to not let it happen again?

I found that simply asking the question often leads to interesting discoveries,
and sometimes triggers a change in the process, tools our refactoring habits.

In our case, I think the main problem is that we had an *implicit dependency*
between the safe and the door.

# A better refactoring

First, let's move the Door class inside the Safe class, and just
forward the calls:


```cpp
class Safe() {
  public:
  Safe(): door_(Door()) {}

  void enterDoorCombination(std::string const& combination) {
    door_.enterCombination(combination);
  }

  void unlockDoor(Key key) {
    door_.unlock(key);
  }

  void openDoor() {
    door_.open();
  }

  private:
  Door door_;
};
```

The code now becomes:

```cpp
void openSafeDoor(Safe& safe) {
  Brain brain;
  brain.thinkReallyHard();
  auto combination = brain.getCombination();
  safe.enterDoorCombination(combination);

  auto correctPocket = findCorrectPocket();
  auto key = correctPocket.key();
  safe.unlockDoor(key);

  safe.openDoor();
}

void safelyStoreDocuments(Safe& safe, std::list<Document> const& documents) {
  openSafeDoor(safe);

  putDocumentsIntoSafe(safe, documents);
}
```

and the problem goes away.

But we can do better! Let's introduce a more generic `open` method to the safe:

```cpp
class Safe() {
  // ...
  void open(std::string const& combination, const Key& key) {
    door_.enterCombination(combination);
    door_.unlock(key);
    door_.open();
  }
}
```

The code now becomes:

```cpp
void openSafe(Safe& safe) {
  Brain brain;
  brain.thinkReallyHard();
  auto combination = brain.getCombination();

  auto correctPocket = findCorrectPocket();
  auto key = correctPocket.key();

  safe.open(combination, key);
}
```

Note how it's now *impossible* to try to use the key without entering the
combination, since the combination and the key are required to call the
`safe.open()` method.

# Better boundaries

I think an other issue with the code is that it was split only by considering
the sequence of events (enter the combination, find the key, unlock the door
...), but without trying to introduce useful abstractions.

Look how we can move code around and get something much more readable:

```cpp
class Safe() {
  // ...
  void open() {
  // same as before
  }

  void putDocuments(std::list<Document> const& documents) {
    for(auto const& document: documents) {
      checkAvailableRoom();
      putDocument(document);
    }
  }

  // ...
}

Key getKey() {
  Pocket correctPocket = findCorrectPocket();
  return correctPocket.key();
}

const std::string getCombination() {
  Brain brain;
  brain.thinkReallyHard();
  return brain.getCombination();
}

int main() {
  Document passport("passport");
  Document idCard("ID card");
  std::list<Document> documents{passport, idCard};

  auto key = getKey();
  auto combination = getCombination();

  Safe safe;
  safe.open(combination, key);
  safe.putDocuments(documents);
}
```

What changed ?

First, we got rid of three methods with 'safe' in their names
(`safelyStoreDocuments`, `openSafe` and `putDocumentsIntoSafe`.

Those names were a clue that those functions actually belonged to the
`Safe` class.

The `Safe` class itself has grown and is now responsible of maintaining invariants
(making sure the door is open and closed, and that there's enough room for all
the documents).

Lastly, `main()` is now only concerned about gathering the various element it needs,
and only calls "high level" methods of the safe. It knows nothing about how the
safe door, or where the key and combination are coming from.

I think it's a much better design.


# Conclusion

Object-oriented programming is hard, C++ is hard, naming things are
important, and thinking about boundaries lead to better code.

Hope you enjoyed my story, see you next time!
