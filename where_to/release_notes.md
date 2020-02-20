## 0.5.0

### New
- Omit cartouche when background is relatively uniform
  ([#14](https://github.com/blairconrad/where-to/pull/14))


## 0.4.0

### Changed
- Stop displaying subject in list mode ([#10](https://github.com/blairconrad/where-to/pull/10))

### Fixed
- Today's recurring appointments not found when run before 00:15 ([#5](https://github.com/blairconrad/where-to/pull/5))
- Duplicates shown when recurring appointment has an exception but for the original day ([#11](https://github.com/blairconrad/where-to/pull/11))


## 0.3.1

### Fixed
- `next` option doesn't always get next meeting ([#2](https://github.com/blairconrad/where-to/pull/2))
- Exceptions to recurring appointments not shown ([#6](https://github.com/blairconrad/where-to/pull/6))

### Additional Items
- Add `test` task, invoked by `poetry run task test`
- Modularize the code a little
- Download get-poetry to `TEMP` directory on AppVeyor
- Add characterization tests for lock mode ([#8](https://github.com/blairconrad/where-to/pull/8))


## 0.3.1-alpha.7

### Additional Items
- Use HTTP Basic authentication for PyPi
- Have poetry publish without interaction


## 0.3.1-alpha.2

### Additional Items
- Remove exact version string test


## 0.3.1-alpha.1

### Additional Items
- Add tools to set version and deploy


## 0.3.0

### Changed
- Make `where-to` the no-console executable and `where-to-console` the
  console-having executable

### New
- Save output to a file (and display it) when there's no console


## 0.2-alpha.1

### New
- A no-console executable


## 0.1.2

### Fixed
- Old appointments linger


## 0.1.1

### Fixed
- Old appointments linger


## 0.1.0

### New
- Initial implementation