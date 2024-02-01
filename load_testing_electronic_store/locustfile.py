from locust import task, run_single_user
from locust import FastHttpUser


class localhost(FastHttpUser):
    host = "http://localhost:8081"
    default_headers = {
        "sec-ch-ua": '"Chromium";v="118", "YaBrowser";v="23", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }

    @task
    def t(self):
        with self.client.request(
            "GET",
            "/docs",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ru,en;q=0.9",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Host": "localhost:8081",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.821 YaBrowser/23.11.2.821 Yowser/2.5 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.client.request(
            "GET",
            "https://browser.translate.yandex.net/v5.10/dist/scripts/addons/tr_page_bundle_with_images.js",
            headers={
                "Referer": "http://localhost:8081/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.821 YaBrowser/23.11.2.821 Yowser/2.5 Safari/537.36",
            },
            catch_response=True,
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://browser.translate.yandex.net/site/api/validate?srv=yabrowser&sid=18c96fee3c805260&url=localhost&",
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "ru,en;q=0.9",
                "origin": "http://localhost:8081",
                "referer": "http://localhost:8081/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.821 YaBrowser/23.11.2.821 Yowser/2.5 Safari/537.36",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://browser.translate.yandex.net/api/v1/tr.json/translate?translateMode=auto&context_title=authentication_service%20-%20Swagger%20UI&id=18c96fee3c805260-0-0&srv=yabrowser&text=Collapse%20operation&text=user&text=post%20%E2%80%8B%2Fauth%E2%80%8B%2Fuser%E2%80%8B%2F&text=%3Cspan%3EPOST%3C%2Fspan%3E%3Cspan%3E%2Fauth%3Cwbr%3E%2Fuser%3Cwbr%3E%2F%3C%2Fspan%3E&text=Create%20User&text=Copy%20to%20clipboard&text=Parameters&text=Try%20it%20out%20&text=No%20parameters&text=Request%20body&text=Request%20content%20type&text=Example%20Value&text=Schema&text=Responses&text=Code&text=Description&text=Links&text=Successful%20Response&text=Media%20type&lang=en-ru&format=html&options=2&version=5.10&",
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "ru,en;q=0.9",
                "origin": "http://localhost:8081",
                "referer": "http://localhost:8081/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.821 YaBrowser/23.11.2.821 Yowser/2.5 Safari/537.36",
            },
        ) as resp:
            pass
        with self.rest(
            "GET",
            "https://browser.translate.yandex.net/api/v1/tr.json/translate?translateMode=auto&context_title=authentication_service%20-%20Swagger%20UI&id=18c96fee3c805260-1-0&srv=yabrowser&text=Media%20Type&text=Controls%20%3Cwbr%3E%20header.&text=No%20links&text=Validation%20Error&lang=en-ru&format=html&options=2&version=5.10&",
            headers={
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "ru,en;q=0.9",
                "origin": "http://localhost:8081",
                "referer": "http://localhost:8081/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.821 YaBrowser/23.11.2.821 Yowser/2.5 Safari/537.36",
            },
        ) as resp:
            pass


if __name__ == "__main__":
    run_single_user(localhost)
