# daily-digest

A scheduled loop with memory (a spine). Once a day it scans this repo for
open TODO comments, compares them against what past runs already reported
(recorded in `progress.md`), and appends a short entry listing **only the
NEW TODOs**. The only state that survives between runs is `progress.md` —
that is what makes the memory work.

## Files

- `daily_digest.sh` — one full run (one beat) of the loop.
- `setup_schedule.sh` — installs the daily 09:00 cron job, logs to `digest.log`.
- `progress.md` — the spine: a dated log of every past run.
- `example.py` — demo file containing sample TODO comments.

## Test it manually (prove the memory works)

```sh
./daily_digest.sh                      # run 1: reports whatever TODOs exist
echo "# TODO: fake task" >> example.py
./daily_digest.sh                      # run 2: reports ONLY the new TODO
```

Then look at the last two entries in `progress.md`: the second entry must
mention only the TODO you just added, not the ones from the first entry.
Run it a third time with no changes and it should say
`No new TODOs since last run.` To start fresh, delete `progress.md` (the
script recreates it).

## Enable the real schedule

```sh
./setup_schedule.sh
```

It adds a cron job running `daily_digest.sh` every day at 09:00, logging
output to `digest.log`, and prints the crontab line so you can confirm it.
Running it twice does not duplicate the job.

## Notes

- The scan skips the project's own machinery (`progress.md`, `README.md`,
  `digest.log`, the two `.sh` scripts) and `.git/`, so the spine and docs
  never pollute the digest.
- A TODO is identified by `path:line` **and** its text, so editing a line
  counts as a new finding.
