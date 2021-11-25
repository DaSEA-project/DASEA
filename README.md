# DASEA

[![Go Build](https://github.com/heyjoakim/DASEA/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/heyjoakim/DASEA/actions/workflows/build.yml) [![Go Report Card](https://goreportcard.com/badge/github.com/heyjoakim/dasea)](https://goreportcard.com/report/github.com/heyjoakim/dasea)

**Da**ta for **S**oftware **E**cosystem **A**nalysis (DASEA)

A continuously updated dataset of software dependencies covering various package manager ecosystems.

Current:

- Conan
- Fpm
- Vcpkg

Access datasets at [DASEA](https://heyjoakim.github.io/DASEA/)

## Executables

### Generate csv files locally

```bash
go run main.go packageManagerName
```

### Create .env file

```bash
cp .env.example .env
```

Populate the .env file with your Zenodo API ACCESS_TOKEN key, where you want the dataset to be published. You can create one [here](https://zenodo.org/account/settings/applications/tokens/new/)

### Publish a new dataset

After you generate the csv files for the package managers, to publish the final dataset, run:

```bash
go run main.go publish-dataset

```

# Contribute

See [CONTRIBUTE.md](https://github.com/heyjoakim/DASEA/blob/main/CONTRIBUTE.md) file

# License

Licensed by the [GNU Affero General Public License v3.0](https://github.com/heyjoakim/DASEA/blob/main/LICENSE)

# Jekyll Homepage

- Follow the [Jekyll installation guide](https://jekyllrb.com/docs/installation/)
- cd into the docs folder
- Run the docs locally:

```bash
  bundle exec jekyll serve
```

Note: if you get a webrick-related [error](https://github.com/jekyll/jekyll/issues/8523), run `bundle add webrick`
