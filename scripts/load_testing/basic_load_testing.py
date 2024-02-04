from locust import HttpUser, between, task

# Super basic load testing, powered by Locust - https://www.locust.io/
# Still useful to get an idea of how the cheap Fly.io server behaves under load :-)


class BasicTestingUser(HttpUser):
    # @link https://docs.locust.io/en/stable/writing-a-locustfile.html
    wait_time = between(1, 5)

    @task
    def display_various_stuff(self):
        self.client.get("htmx/no-selection/")
        self.client.get("htmx/daily-challenge/modals/stats/")
        self.client.get("htmx/daily-challenge/modals/help/")
        self.client.post(
            "htmx/daily-challenge/restart/do/",
            headers={
                "X-CSRFToken": self.csrf_token,
            },
        )

    def on_start(self):
        self.client.get("")
        self.csrf_token = self.client.cookies["csrftoken"]
