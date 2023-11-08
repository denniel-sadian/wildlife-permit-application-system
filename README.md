# DENR-PENRO Online System

A capstone project for the DENR-PENRO's wildlife permit management and application.

**How to run:**
1. Download and install Docker.
2. Clone this repository.
3. Start the app by running: `docker-compose up`
4. Apply database migrations (on a separate terminal): `docker-compose exec -it app python manage.py migrate`.
5. Visit http://localhost:8000
