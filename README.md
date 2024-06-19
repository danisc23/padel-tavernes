# Padel-Tavernes

Originally this was a Flask api that scraped the [Esport En Tavernes Blanques](https://www.esportentavernesblanques.es/) website to get the padel (and other sports) bookings.
Currently it scrapes all the known websites from [Webs de padel](https://www.websdepadel.com/) platform that allows to find the available courts to play padel in one place. So the project name is already outdated, 🥳.

The scraped platform has a some issues that this project tries (or will try) to solve:
- Each club has its own website and app to book the courts, so you need to check all the websites 1 by 1 to find the available courts.
- The website only shows the available courts for 1 day, so you need to check day by day to find the available courts.
- Don't have any filter to find only the available courts, so you need to navigate through all the courts to find the available ones.

The motivation for this project was just to have fun and to not forget about python since I'm not using it these months. But also I wanted to play around [Flask](https://flask.palletsprojects.com/en/2.0.x/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) since I never used these before. Also I must recognice that every time I go back to Valencia and I want to play padel [Playtomic](https://www.playtomic.io/) is always empty since every club is using their own website and apps to book the courts, so I wanted to create a tool that could help me to see all the available courts in one place.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Development](#development)
  - [Running Locally](#running-locally)
  - [Testing](#testing)
  - [Linting](#linting)
- [Deployment](#deployment)
  - [Using Docker Compose](#using-docker-compose)
- [Contributing](#contributing)

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:

- [Docker](https://www.docker.com/get-started) installed on your system.
- [Poetry](https://python-poetry.org/docs/) for managing Python dependencies.
- [Pre-commit](https://pre-commit.com/) for linting and formatting.
- [Python](https://www.python.org/downloads/) 3.12 or higher.

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/danisc23/padel-tavernes.git
   ```

2. Change to the project directory:

   ```bash
   cd padel-tavernes
   ```

3. Install the project dependencies using Poetry:

   ```bash
   poetry install
   ```

4. Install pre-commit hooks to ensure consistent code style:

   ```bash
   pre-commit install
   ```

## Development

### Running Locally

To run the application locally, use Poetry's virtual environment:

```bash
poetry shell
python run.py
```

or

```bash
poetry run python run.py
```

The docs will be available at `http://localhost:8000/docs/`.

### Testing

To run the tests, execute the following command:

```bash
poetry run pytest .
```

### Linting

Linting is done using pre-commit hooks. Before committing your code, linting and formatting checks will run automatically. If there are any issues, pre-commit will prevent the commit and inform you of the problems that need to be fixed.

You can also run the pre-commit checks manually using the following command:

```bash
pre-commit run --all-files
```

## Deployment

### Using Docker Compose

To run the application in a Docker container, follow these steps:

1. Build the Docker image:

   ```bash
   docker-compose build
   ```

2. Start the Docker container:

   ```bash
   docker-compose up -d
   ```

The Flask app should now be accessible at `http://localhost:8000/docs/`.

## Contributing

Honestly, this is a project that I did in a couple of hours just to entertain myself and to not forget about python since is my main language but I'm not using it these months. But if you want to contribute, feel free to do it. Just fork the repository, make your changes and submit a pull request.

Maybe would be interesting to extract some other information like statistics about wich courts are more used, sport is played the most, etc. (Done)
Or would be interesting to see all the available courts for the different websites like [Playtomic](https://www.playtomic.io/). (Also Done 🤭)
Would be super cool to create a web that implements this api.
Also there are *modern* alternatives to [Webs de padel](https://www.websdepadel.com/) like [Matchpoint By Matchi](https://tpcmatchpoint.com/) that could be interesting to scrape and show in the same place.

Take in mind that the [Webs de padel](https://www.websdepadel.com/) platform is quite old and padel clubs are moving to other platform so this project could be deprecated soon.

### TODO
- [x] Scrape websites from [Webs de padel](https://www.websdepadel.com/) platform.
- [ ] Create and updatable db to easily increase the number of clubs (currently is hardcoded).
- [ ] Improve the way filters are defined (currently is hardcoded, each club has different sports).
- [ ] To improve Swagger documentation would be nice to use models and arguments definitions in the good way.
- [x] Add the capability to filter by geolocation (I should even force this since the amount of clubs is increasing and I don't want to DDOS the websites).
- [ ] Cache the results to avoid scraping the websites every time (At least for half an hour, same reason as before).
- [ ] Parallelize the scraping to make it faster.
- [ ] Create a web that implements this api.
