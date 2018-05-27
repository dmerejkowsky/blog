---
authors: [dmerej]
slug: a-booleans-story
date: 2018-05-18T13:50:38.605961+00:00
draft: false
title: "A boolean's story"
tags: [rust]
---

[Earlier this month]({{< ref "post/0068-introducing-rusync.md" >}}) I told you
about my pet project in Rust.

As a reminder, it's a tool named rusync which contains some of the
functionality offered by the `rsync` command-line tool.

Today I'd like to talk about a feature I've added recently, and take this
opportunity to show you a few principles of good design along the way.

You can find the code on [github](https://github.com/dmerejkowsky/rusync) and
download it from [crates.io](https://crates.io/crates/rusyn://crates.io/crates/rusync).

# The algorithm

You run rusync by calling it with a source and destination directory, like so:

```
$ rusync src dest
```

The algorithm is pretty straightforward:

* Recurse through all directories and files in the `src` directory
* For each source file (for instance `src/foo/bar.txt`), check if the destination file
  (`dest/foo/bar.txt` in this case) exists. If it *does* exist, get its `mtime` (that is, the
  date it was last modified). Then, if the source is more recent than the destination, or if
  the destination is missing, proceed and copy the whole contents of
  `src/foo/bar.txt` to `dest/foo/bar.txt`.

One of the issues I had to deal with is the preservation of permissions.
Suppose one of the files is executable, let's say `src/foo/bar.exe`, then the
destination (`dest/foo/bar.exe`) should be executable too.

So, after the destination file has been written, we should apply the necessary
transformations so that the permissions of the destination file match the
permissions of the source file.

# The code

Here's what the implementation looked like at the time.

{{< note >}}
There's a bug waiting to happen in the following code, can you find it ?
{{</ note >}}

Let's start by `main()`:

```rust
#[derive(Debug, StructOpt)]
#[structopt(name = "rusync")]
struct Opt {
    #[structopt(parse(from_os_str))]
    source: PathBuf,

    #[structopt(parse(from_os_str))]
    destination: PathBuf,
}

fn main() {
    let opt = Opt::from_args();
    let source = &opt.source;
    let destination = &opt.destination;
    let mut syncer = Syncer::new(&source, &destination);
    syncer.sync()?;
}
```

We declare a struct `Opt` which will contain our command line options, then in
`main()` we parse the command line arguments and instantiate a new `Syncer`
object.

Here are the relevant parts of the `Syncer` implementation:

```rust

impl Syncer {
    fn new(source: &Path, destination: &Path) -> Syncer {
        Syncer {
            source: source.to_path_buf(),
            destination: destination.to_path_buf(),
            // ...
        }
    }


    fn sync(&mut self) -> io::Result<()> {
        let top_dir = &self.source.clone();
        self.walk_dir(top_dir)?;
        Ok(())
    }

    fn walk_dir(&mut self, subdir: &Path) -> io::Result<()> {
        for entry in fs::read_dir(subdir)? {
            let entry = entry?;
            let path = entry.path();
            if path.is_dir() {
                let subdir = path;
                self.walk_dir(&subdir)?;
            } else {
                self.sync_file(&entry)?;
            }
        }
        Ok(())
    }

    fn sync_file(&mut self, entry: &DirEntry) -> io::Result<()> {
        let rel_path = get_rel_path(&entry.path(), &self.source)?;
        let parent_rel_path = rel_path.parent();
        let to_create = self.destination.join(parent_rel_path);
        fs::create_dir_all(to_create)?;

        let src_entry = entry::Entry::new(&desc, &entry.path());

        let dest_path = self.destination.join(&rel_path);
        let dest_entry = entry::Entry::new(&desc, &dest_path);
        fsops::sync_entries(&src_entry, &dest_entry)?;
        Ok(())
    }

```

As you can see, the bulk of the work is done by the `sync_file` function, which
calls `fsops::sync_entries` with a `Entry` type.

The `Entry` type is a container for the file path and its metadata. Reading metadata
about the file (such as its `mtime`) is expensive, so we do that once in the
`Entry::new()` function and the rest of the code can then use the public functions of the `Entry` struct to retrieve info about the file in question.

```rust
pub struct Entry {
    path: PathBuf,
    metadata: Option<fs::Metadata>,
    exists: bool,
}

impl Entry {
    pub fn new(description: &str, entry_path: &Path) -> Entry {
        let metadata = fs::metadata(entry_path).ok();
        Entry {
            metadata: metadata,
            path: entry_path.to_path_buf(),
            exists: entry_path.exists(),
        }
    }

    pub fn path(&self) -> &PathBuf { &self.path }
    pub fn exists(&self) -> bool { self.exists }

    pub fn metadata(&self) -> Option<&fs::Metadata> {
        self.metadata.as_ref()
    }
}
```

Finally, let's take a look at the `sync_entries` function:

```rust
const BUFFER_SIZE: usize = 100 * 1024;

pub fn sync_entries(src: &Entry, dest: &Entry) -> io::Result<()> {
    let more_recent = more_recent_than(&src, &dest)?;
    if more_recent {
        return copy_entry(&src, &dest);
    }
    Ok(())
}

pub fn copy_entry(src: &Entry, dest: &Entry) -> io::Result<()> {
    let src_path = src.path();
    let src_file = File::open(src_path)?;
    let dest_file = File::create(dest_path)?;
    let mut buffer = vec![0; BUFFER_SIZE];
    loop {
        let num_read = src_file.read(&mut buffer)?;
        if num_read == 0 {
            break;
        }
        dest_file.write(&buffer[0..num_read])?;
    }
    copy_perms(&src, &dest)?;
}

fn copy_perms(src: &Entry, dest: &Entry) -> io::Result<()> {
    let src_meta = &src.metadata();
    let src_meta = &src_meta.expect("src_meta was None");
    let permissions = src_meta.permissions();
    let dest_file = File::create(dest.path())?;
    dest_file.set_permissions(permissions)?;
    Ok(())
}
```

As you can see, the `sync_entries` function takes care of copying the source
file contents to the dest file chunk by chunk, and then calls `copy_perms()`.

# A new option

After a while, it occurred to me that rusync will be annoying to use in case we
copy from an `ext4` partition to a `fat32` partition.

Indeed, Linux cannot set permissions on a `fat32` partitions, so the code from
`copy_perms` would surely fail in this case.

I decided what I needed was a flag on the command line so that users of rusync
could choose to turn off the "copy permissions" feature.

Well, this does not seem to hard, does it ? We just need to pass around a
boolean called `preserve_permissions`  all the way from the `Opt` struct in
`main` to the `sync_entries` in function, across the `Syncer` struct.

Let's do that!

First, let's adapt `main.rs`:

{{< highlight rust "hl_lines=4 13 16" >}}

struct Opt {

    #[structopt(long = "no-perms")]
    no_preserve_permissions: bool,

    // ...
}

fn main() {
    let opt = Opt::from_args();
    let source = &opt.source;
    let destination = &opt.destination;
    let preserve_permissions = !opt.no_preserve_permissions;

    let mut syncer = Syncer::new(&source, &destination);
    syncer.preserve_permissions(preserve_permissions);

    // ...
}
{{</ highlight >}}

Then let's adapt the `Syncer`:


{{< highlight rust "hl_lines=7 11-13 17" >}}
impl Syncer {
    fn new(source: &Path, destination: &Path) -> Syncer {
        Syncer {
            source: source.to_path_buf(),
            destination: destination.to_path_buf(),
            // ...
            preserve_permissions: true,
        }
    }

    pub fn preserve_permissions(&mut self, preserve_permissions: bool) {
        self.preserve_permissions = preserve_permissions;
    }

    fn sync_file(&mut self, entry: &DirEntry) -> io::Result<()> {
        // ...
        fsops::sync_entries(&src_entry, &dest_entry, preserve_permissions);
        Ok(())
    }

{{</ highlight >}}

And then let's adapt `sync_entries` and `copy_entry`:

{{< highlight rust "hl_lines=1-2 5 10-11 16-18" >}}
pub fn copy_entry(src: &Entry, dest: &Entry,
                   preserve_permissions: bool,) -> io::Result<()>  {
    let more_recent = more_recent_than(&src, &dest)?;
    if more_recent {
        return copy_entry(&src, &dest, preserve_permissions);
    }
    Ok(())
}

pub fn copy_entry(src: &Entry, dest: &Entry,
                  preserve_permissions: bool) -> io::Result<()> {
    let src_path = src.path();
    let src_file = File::open(src_path)?;

    // ...
    if preserve_permissions {
      copy_perms(&src, &dest)?;
    }
}

{{</ highlight >}}


Now we run the tests, and it looks like nothing broke. Hooray!


# Time for refactoring

There are several things we can change to make the code more readable.

First, we can get rid of the double negative in `main.rs`:

```patch
impl Opt {
struct Opt {
    #[structopt(long = "no-perms")]
    no_preserve_permissions: bool,

    // ..
}

+ impl Opt {
+     fn preserve_permissions(&self) -> bool {
+         !self.no_preserve_permissions
+     }
+ }

fn main() {
    let opt = Opt::from_args();
    let source = &opt.source;
    let destination = &opt.destination;
-   let preserve_permissions = !opt.no_preserve_permissions;
+   let preserve_permissions = opt.preserve_permissions();
    let mut syncer = Syncer::new(&source, &destination);
    syncer.preserve_permissions(preserve_permissions);
  }
}
```
Yeah, I know it's a little change, but it's the kind of little details that
matter in the long run. Double negatives are just as hard to understand in
plain English as in code.

Then we have all these functions that take a boolean parameter.

As [Uncle Bob](https://blog.cleancoder.com/) would tell you, whenever you have
a function that takes a boolean, you almost always want two functions instead.

So let's think about our `preserve_permissions` boolean.

Turns out we can split `sync_entries` in two. One that only does the copy, and
the other one that deals with permissions preservation.

We'll keep the `preserve_permission` field in the `Syncer`, and only call the
second function if we need to.

Let's have a look at the patch:

```patch
- pub fn copy_entry(src: &Entry, dest: &Entry,
-                   preserve_permissions: bool,) -> io::Result<()>  {
+ pub fn copy_entry(src: &Entry, dest: &Entry) -> io::Result<()> {

  // ..

-    if preserve_permissions {
-        copy_permissions(&src, &dest);
-    }
  Ok(())
}
- pub fn sync_entries(src: &Entry, dest: &Entry,
-                      preserve_permissions: bool) -> io::Result<()> {
+ pub fn sync_entries(src: &Entry, dest: &Entry) -> io::Result<(SyncOutcome)> {
     if more_recent {
-        return copy_entry(&src, &dest, preserve_permissions);
+        return copy_entry(&src, &dest);
}

impl Syncer {

    fn sync_file(*mut self, entry: &DirEntry) -> io::Result<()> {

         let dest_path = self.destination.join(&rel_path);
-        fsops::sync_entries(&src_entry, &dest_entry, self.preserve_permissions)?;
+        fsops::sync_entries(&src_entry, &dest_entry)?;
+        if self.preserve_permissions {
+            fsops::copy_permissions(&src_entry, &dest_entry)
+          }
}
```

It seems we just moved the logic about permissions preservation from the low-level
`fsops` module, to the high-level `Syncer` module, but the consequences of this refactoring
may be more profound than you think.

# A new design

Note how the functions in `fsops` now know *nothing* about the command-line flags.

That's us trying to adhere to Single Responsibility Principle. The <abbr
title="Single Responsibility Principle">SRP</abbr> more or less states that
each module should only have one reason to change.

Code in `syncer.rs` will have to change if we want to customize the *behavior* of `rusync`
(like deleting the extraneous files in the destination folder). On the other hand, code in
`fsops.rs` will have to change if we want to modify low-level *implementation* details of `rusync`
(like using a more efficient algorithm like rsync does).

Note that in the first case, we'll of course have to add code in `fsops.rst` to
delete files or directories, but we are OK with it because the code will
likely don't have to be *modified*, we'll just have to *add more functions*.
(That's an other principle at play here called the Open/Close Principle).

Anyway, found the bug yet?

# The bug

I actually discovered the "bug waiting to happen" I talked about in the
beginning when I re-ran the test suite after I performed
the refactoring I just discussed. One of the tests started failing.

Can you try and find it just by looking at the patches above ?

{{< note >}}
There is a clue about the bug in one of the previous post of this blog.
{{</ note >}}

If you want to find out, click on the "spoiler" below.

{{< spoiler >}}

It's the same kind of bug I mentioned in the [non-isomorphic C++ refactoring
article]({{< ref "post/0051-non-isomorphic-cpp-refactoring.md" >}}).

You see, in Rust some types implement the `Drop` trait, and have a `.drop()`
method called when they go out of scope.

In our case, *before* our refactoring, the dest file was created twice. Once in
the `copy_entry()` function, and an other time in the `copy_perms()` function.
Usually, `File::create` truncates the file, but when the first file handle was
destroyed, its contents were magically preserved. (Software is weird sometimes)

After the refactoring, the second `File:;create()` was called after the first
file handle was closed, and the destination filed ended up empty (but with the
correct permissions ...)


{{</ spoiler >}}
