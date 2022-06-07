- [Ideas](#ideas)
  - [Task Control Block](#task-control-block)
    - [Pros](#pros)
    - [Cons](#cons)
  - [Simplify Human Hash](#simplify-human-hash)
  - [Event Driven vs Polling](#event-driven-vs-polling)
  - [Add .editorconfig](#add-editorconfig)
  - [Add .pre-commit-config.yaml](#add-pre-commit-configyaml)
  - [Sub-classing Process](#sub-classing-process)
  - [Better Process Naming](#better-process-naming)
  - [File Organization](#file-organization)

# Ideas

This document is intended to hold ideas for future improvements of the code.  For when one doesn't have time to
implement anything, but does want to explore an idea in the future.

## Task Control Block

Currently, a task is defined using a dictionary of data, which is passed around.  Though this works, using a
dedicated class (perhaps a dataclass) with fields could be useful.

### Pros

- IDEs will be able to autocomplete field names
- Adding a new field or configuration requires modifying only one place
- Default values can be set in only 1 place

### Cons

- Pretty large amount of code to change
- Perhaps more memory usage

## Simplify Human Hash

The human hash is a great way to convert a hard to remember UUID into an more friendly name.  But
I think the current code for this is more complicated than necessary.  The `humanize` module level
function is also called a lot, recalculating what is likely the same UUID value to a name often.

- The word list is configurable, but never is changed
- The compress and humanize methods also are configurable, but are never changed

I would consider a class (perhaps a dataclass) which has the following fields:

- id - the actual UUID
- digest - the hex formatted digest of the UUID
- name - the nice human name of the UUID

The UUID is created once, the dependent fields are created once and the object is frozen.

## Event Driven vs Polling

I'm unsure how yet to do this, or if it is all possible, but changing the architecture to be more
event driven instead of polling for work would help the idle resource usage.

Right now, the Sentinel guard loop runs every GUARD_CYCLE seconds, checking if workers, the pusher and monitor
are still alive.  Could [multiprocessing.connection.wait](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.connection.wait)
with a timeout work instead?  This may also require usage of Connection objects, to indicate work is completed?

Then for Schedule tasks, maybe a threading [Timer](https://docs.python.org/3/library/threading.html#timer-objects) can trigger running a
task in the future, instead of polling continuously?  Set the future timeout in seconds, to trigger checking the database for scheduled tasks?

This would be a very large change in the architecture, but if it (or even potions of it) are possible, it would be
a much better solution than consistently polling and eating up cycles.

## Add .editorconfig

Pretty easy, adding an .editorconfig file will help keep the styling consistent across multiple authors.

## Add .pre-commit-config.yaml

Along the same idea as above, adding a pre-commit configuration will help enforce styling and formatting,
as well as catching come issues early.

Depending on the hooks, this could result in larger code changes, but they should only be stylistic.

## Sub-classing Process

Right now, the cluster uses `multiprocessing.Process` with a target quite a bit.  I feel it would be cleaner and not too hard to instead
sub-class `Process` and move the work done in functions internal to the class.

This could also benefit from having a base class, which store anything common (say Events, Queues, etc).

## Better Process Naming

Currently, spawned processes don't set their name, and so use the default scheme, which takes from the parent process.
An improvement might be to name tasks, based on their function (Worker, Pusher, Monitor) and their generation (giving
an idea of how many times a task has been re-incarnated or recycled)

## File Organization

The `cluster.py` file contains a lot more than Cluster.  Simplify the file by moving other classes to their own
files and common functionality to an appropriate file as well.
