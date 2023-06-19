import requests, random, threading, string, json, capsolver
from capmonster_python import RecaptchaV2Task
proxies_genned = 0
class webshare:
    def __init__(self, proxyless: False, log_rotating: False, captcha_key: str, captcha_service: str='capmonster') -> None:
        self.proxies_genned = 0
        self.proxyless = proxyless
        self.captcha_key = captcha_key
        self.log_rotating = log_rotating
        self.service = captcha_service
        self.session = requests.Session()

        self.session.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }

        if not proxyless:
            self.proxies = [prox.strip() for prox in open("proxies.txt")]; self.prox = random.choice(self.proxies)
            self.session.proxies = {
                'https': f'http://{self.prox}',
                'http': f'http://{self.prox}'
            }
    
    @staticmethod
    def solve_captcha(key: str, service: str):
        if service == "capmonster":
            capmonster = RecaptchaV2Task(key)
            task_id = capmonster.create_task("https://webshare.io", "6LeHZ6UUAAAAAKat_YS--O2tj_by3gv3r_l03j9d")
            result = capmonster.join_task_result(task_id)
            return result.get("gRecaptchaResponse")
        else:
            capsolver.api_key = key
            return capsolver.solve({
                        "type": "ReCaptchaV2TaskProxyLess",
                        "websiteURL": "https://webshare.io",
                        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                        "websiteKey": "6LeHZ6UUAAAAAKat_YS--O2tj_by3gv3r_l03j9d"
                    })['gRecaptchaResponse']
        
    def register(self):
        print("Solving Recaptcha")
        captcha_key = webshare.solve_captcha(service=self.service, key=self.captcha_key)
        if captcha_key == None:
            return webshare(self.proxyless,self.log_rotating).begin()
        print("Solved Captcha")
        url = 'https://proxy.webshare.io/api/v2/register/'
        payload = {"email": f"{''.join(random.choice(string.ascii_letters) for x in range(random.randint(10, 14)))}@gmail.com","password":f"Joker{random.randint(2000, 5000)}!","tos_accepted":True,"recaptcha": captcha_key}
        response = self.session.post(url, json=payload)
        self.session.cookies = response.cookies
        try:
            return response.json()['token']
        except:
            #print("Error creating webshare acct")
            return webshare(self.proxyless,self.log_rotating).begin()
        
    def download_proxies(self):
        url = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=10'
        for proxy in self.session.get(url).json()['results']:
            if self.log_rotating:
                with open("output.txt", 'a+') as f:
                    f.write(f"{proxy['username']}-rotate:{proxy['password']}@p.webshare.io:80\n")
                    print("Genned 1GB rotating proxy")
                    break
            else:
                with open("output.txt", 'a+') as f:
                    f.write(f"{proxy['username']}:{proxy['password']}@{proxy['proxy_address']}:{proxy['port']}\n")
        print(f"Genned 1GB 10 static proxies")
        return
    
    def begin(self):
        token = self.register()
        print("Created Webshare Account")
        self.session.headers['Authorization'] = f"Token {token}"
        self.download_proxies()
        return webshare(self.proxyless, self.log_rotating).begin()

if __name__ == "__main__":
    with open("config.json") as f:
        data = json.load(f)
        choice1 = "y" if data['proxyless'] is True else "n"
        captcha_key = data['captcha_apikey']
        captcha_service = data['captcha_service']
    choice2 = input("static/rotating (1/2): ")
    for i in range(int(input("threads (for proxyless recommended is 15 or below): "))):
        ws = webshare(True if choice1.lower() == 'y' else False, True if choice2.lower() == '2' else False, captcha_key, captcha_service)
        threading.Thread(target=ws.begin).start()