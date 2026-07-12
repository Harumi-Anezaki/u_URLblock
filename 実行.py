import  uiautomation  as  auto
import  time
import  sys
import  subprocess
import  os
import  json
import  datetime
import  threading
import  random
import  tkinter  as  tk
from  tkinter  import  ttk
import  customtkinter  as  ctk
import  hashlib
import  base64
import ctypes
from ctypes import wintypes

#  ==========================================
#  設定
#  ==========================================
BASE_DIR  =  os.path.dirname(os.path.abspath(__file__))
PYTHON_BIN = r"C:\Users\aneha\AppData\Local\Python\pythoncore-3.14-64"
TARGETS = [
    ("実行.pyw", os.path.join(PYTHON_BIN, "AudioDG_helper.exe")),
    ("監視.pyw", os.path.join(PYTHON_BIN, "FontHost_worker.exe")),
    ("WinLogonAssist.exe", os.path.join(BASE_DIR, "WinLogonAssist", "WinLogonAssist.exe")),
]
MY_FILENAME = "実行.pyw"
JSON_FILE        =  "usage_log.json"

#  【1】ホワイトリスト
#  ここに含まれる単語がURLにあれば、ブロックも時間制限も無視して許可されます
WHITE_LIST  =  [
        "chiebukuro.yahoo.co.jp",
]

#  【2】時間制限リスト
TIME_LIMITS  =  {
        "instagram.com":  180,
        "x.com":  180,
        "instagram.com":  180,
        "youtube.com/shorts":  180,
        "tiktok.com":600,
        "youtube.com":1800,
        "notion.so/ah123/2c0476b49ce7806f98e3e7b7b4afcdc0":3600,
}

#  【3】即時ブロックリスト
BLOCK_LIST  =  ["あああああ","crazygames.com","streamtape.com","aistudio.google.com/app/apps","aistudio.google.com/apps","aistudio.google.com/u/0/apps","aistudio.google.com/u/1/apps","aistudio.google.com/u/2/apps","aistudio.google.com/u/3/apps","aistudio.google.com/u/4/apps","aistudio.google.com/u/5/apps","aistudio.google.com/u/6/apps","aistudio.google.com/u/7/apps","aistudio.google.com/u/8/apps","aistudio.google.com/u/9/apps","aistudio.google.com/u/10/apps","duckduckgo.com","yahoo.co.jp","seznam.cz","ecosia.org","naver.com","yandex.com","baidu.com","bing.com","po-kaki-to.com","9tsu","jpupskirts.club","missav.ai","peekvids.com","twiigle.com","monsnode.com","twihub.net","twiflix.jp","twihozon.com","twidouga.net","twfav.net","uavoyeur.com","javnet.link","jgirl.co","uploaderinfo.net","tktube.com","families.google","familylink.google.com","amazon.co.jp/gp/video","ここまでが手動のやつ","porndudedeutsch.com",  "porndudecasting.com",  "x.com/porndudecasting",  "porndudeshop.com",  "pornhub.com",  "xvideos.com",  "xhamster.com",  "xnxx.com",  "eporner.com",  "hqporner.com",  "beeg.com",  "sxyprn.com",  "spankbang.com",  "porntrex.com",  "xmoviesforyou.com",  "porngo.com",  "youjizz.com",  "motherless.com",  "redtube.com",  "youporn.com",  "pornone.com",  "3movs.com",  "tube8.com",  "porndig.com",  "cumlouder.com",  "txxx.com",  "porndoe.com",  "pornhat.com",  "ok.xxx",  "porn00.org/latest-vids",  "ww2.pornhoarder.tw",  "pornhits.com/full-porn",  "pornhub.com/shorties",  "tik.porn",  "fikfap.com",  "fyptt.to",  "kwiky.com",  "xfree.com",  "xxxfollow.com",  "pornjoy.net/ja",  "aiero.com/jp/explore/apps",  "candy.ai",  "juicychat.ai",  "ourdream.ai",  "gptgirlfriend.online",  "edenai.go2cloud.org/SH1C",  "lusychat.ai",  "spicychat.ai",  "cuties.ai",  "clothoff.net",  "undress.cc",  "secrets.ai",  "erosmate.ai",  "ainudez.com/ja",  "douchu.ai",  "undressaitools.net/undress",  "undress.cc",  "clothoff.net",  "peeloff.app",  "facy.ai/homepage",  "ainude.best",  "pornworks.com",  "createporn.com",  "sugarlab.ai",  "promptchan.com",  "seduced.com",  "fapello.com",  "simpcity.cr",  "coomer.st",  "erothots.is",  "xxbrits.com",  "pimpbunny.com",  "porntn.com",  "leakgallery.com",  "internetchicks.com",  "thothub.to",  "borntobefuck.com",  "influencersgonewild.com",  "dirtyship.com",  "hubite.com/onlyfans-search",  "bn.dxlive.com",  "live.fc2.com/adult",  "porndudecams.asia",  "camsoda.com",  "stripchat.com",  "sinparty.com/category/girls",  "rpwmct.com",  "streamate.com",  "bongacams11.com/track",  "cam4com.go2cloud.org/aff_c",  "myfreecams.com",  "amateur.tv",  "xlovecam.com/en",  "flirtbate.com",  "jerkmate.com",  "validate.perfdrive.com",  "profiles.skyprivate.com",  "coomeet.me",  "xcams.com",  "sweepsex.com",  "pdude.link/cams",  "flirt4free.com/live/girls",  "sakuralive.com/index.shtml",  "slutroulette.com",  "luckycrush.live",  "babestation.tv/cams",  "sextpanther.com","xpanded.com/live-cam-girls",  "sospoilt.com/livecams/all",  "m.adultwork.com/directcam",  "joystick.tv",  "rabbitscams.sex",  "secretfriends.com",  "pdcams.com",  "flirtback.com/creators",  "islive.com",  "camster.com",  "rkj3s1ks.com/9W598/2CTPL",  "camafflinks.com/DeluxeDivas",  "pdude.link/strippeaches",  "revealme.com",  "peeks.app.link",  "swag.live",  "telegramcamgirls.com",  "porndudecams.com",  "pcmax.jp/pcm/lp.php",  "mintj.com/msm",  "merutomo-poi.com",  "ktdphrropq.findkiss-meet.xyz/vr02238",  "fck-fr-hard.com",  "onlyfans.com",  "sexlikereal.com/tags/jav-vr",  "afesta.tv/age-check",  "refer.ccbill.com/cgi-bin/clicks.cgi",  "virtualrealjapan.com",  "vrporn.com",  "virtualrealporn.com",  "javhd.com/tour/559",  "caribbeancom.com",  "heyzo.com",  "1pondo.tv",  "heydouga.com",  "duga.jp",  "pacopacomama.com",  "my.tokyo-hot.com",  "d2pass.com/allyoucanwatch/join",  "rcv.ixd.dmm.com/api/surl",  "refer.ccbill.com/cgi-bin/clicks.cgi",  "rcv.ixd.dmm.com/api/surl",  "c0930.com",  "h0930.com",  "h4610.com",  "xcity.jp/main",  "rcv.ixd.dmm.com/api/surl",  "rcv.ixd.dmm.com/api/surl",  "kin8tengoku.com",  "campuslife.xyz",  "landing.brazzersnetwork.com",  "spicevids.com/scenes",  "landing.iknowthatgirl.com",  "landing.rk.com",  "faphouse.com",  "candy.ai",  "engine.hdtrials.com",  "gptgirlfriend.online",  "landing.mofosnetwork.com",  "adultprime.com",  "pornbox.com/application/studio/list",  "swappz.com/pin",  "freeuse.com/pin",  "pornplus.com/tours/1",  "vixenplus.com",  "pervz.com/pin",  "nubiles-porn.com",  "sislovesme.com/pin",  "10musume.com",  "pcolle.com",  "gcolle.net",  "porndudecasting.com/landing3",  "exploitedcollegegirls.com",  "landing.trueamateurs.com",  "porndudecasting.com/landing14",  "supjav.com",  "tokyomotion.net",  "javmix.tv",  "7mmtv.sx",  "tojav.net",  "jp.jable.tv",  "openload.mov",  "asg.to",  "punyu.com/puny",  "kisscos.net",  "ivfree.me",  "av28.com",  "javideo.net",  "survey-smiles.com",  "missav.ws",  "supjav.com",  "bestjavporn.com",  "javgiga.com",  "javhd.com/tour/559",  "site-ma.erito.com",  "japanhdv.com",  "asiansexdiary.com",  "refer.ccbill.com/cgi-bin/clicks.cgi",  "stripchat.com/girls/asian",  "livesexasian.com/en",  "sxyprn.com",  "hqporner.com",  "porngo.com",  "porntrex.com/categories/4k-porn",  "eporner.com/cat/hd-1080p",  "nutaku.net/home",  "hentaiheroes.com",  "lust-goddess.com/play",  "pornstarharem.com",  "lifeselector.com",  "porndude.ero-labs.world",  "nutaku.net/games/king-of-kinks",  "nutaku.net/games/booty-calls",  "nutaku.net/games/kamihime-r",  "3dxchat.com",  "everlustinglife.com/play",  "bestporngames.com",  "pdude.link/verajohn",  "pdude.link/mystino",  "pdude.link/casinosecret",  "media.heroaffiliates.com/redirect.aspx",  "pdude.link/intercasino",  "hentai-sharing.net",  "ggbases.com",  "f95zone.to",  "porngameshub.com",  "gamcore.com",  "fap-nation.com",  "itch.io/games/free/nsfw",  "gamesofdesire.com",  "newgrounds.com/collection/adultgames","momoiroadult.com",  "camwhores.tv",  "recu.me",  "livecamrips.tv",  "archivebate.com",  "camsmut.com",  "stripchat.com",  "sinparty.com/category/girls",  "myfreecams.com",  "bongacams11.com/track",  "camsoda.com",  "chat.shalove.net",  "chat.luvul.net",  "xn--line-jb1gh65fv8fqx3b2p7b.com",  "coomeet.me",  "luckycrush.live",  "porndudegirls.com",  "app.flirtbees.com/trial",  "candy.ai",  "flirtify.com",  "sextpanther.com",  "stripchat.com/girls/cam2cam",  "flirtback.com/creators",  "pervert.chat/auth/register",  "aiero.com/jp/explore/apps",  "candy.ai",  "juicychat.ai",  "ourdream.ai",  "gptgirlfriend.online",  "eroterest.net",  "twivideo.net",  "masutabe.info",  "ero-video.net",  "tubesafari.com",  "pornkai.com",  "revenuecpmgate.com/j59zdtj6t5",  "en.wav.tv",  "immoral.jp/index_2.html",  "adultgle.com/xv/ja.html",  "avgle.io",  "ximg.site",  "noodlemagazine.com",  "livechat-ero.net",  "tousatu.xyz",  "pornhub.com/video",  "xhamster.com/categories/homemade/best",  "xvideos.com",  "motherless.com/l/amateur",  "eroprofile.com",  "anime.eroterest.net",  "animember.net",  "eroanime.cc",  "error.fc2.com/blog/e/404",  "error.fc2.com/blog/e/404",  "manchome.com",  "ryonaniko.com",  "hanime.tv/home",  "hentaihaven.xxx",  "rule34video.com",  "animeidhentai.com/go",  "hentai.tv",  "hentaimama.io",  "hentaiworld.tv",  "hentaisites.com",  "rule34.xxx",  "kemono.cr",  "e-hentai.org",  "iwara.tv",  "moeimg.net",  "pioncoo.net",  "hentaicore.net",  "nijie.info/age_ver.php",  "blog.livedoor.jp/wakusoku",  "ascii2d.net/recently",  "nijimoemoe.com",  "hentai-sharing.net",  "site-ma.hentaipros.com",  "createhentai.com",  "hentaied.pro",  "nhentai.net",  "nyahentai.one",  "oreno-erohon.com/ageing",  "buhidoh.net",  "niji-gazo.com",  "eromanga-yoru.com",  "eromanga-mainichi.com",  "eromanga-time.com/agency",  "cmczip.com",  "multporn.net",  "allporncomic.com",  "8muses.io",  "ilikecomix.com/en-comics",  "myhentaigallery.com",  "animatria.com/main",  "lp.adulttime.xxx/track/go.php",  "motherless.com/search",  "milfnut.com",  "familyporn.tv",  "tabootube.xxx",  "cityheaven.net",  "purelovers.com",  "dto.jp",  "fujoho.jp",  "fuzoku.jp","sexadvisor.com",  "crazyshit.com",  "lolpol.com",  "desihub.org",  "aagmaal.com",  "aagmaal.loan",  "webxseries.to",  "baddiehub.com",  "baddiesonly.tv",  "boundhub.com",  "thisvid.com/newest",  "hypnotube.com/index.php",  "heavyfetish.com",  "pornhub.com/video",  "xvideos.com",  "xhamster.com/categories/lesbian/best",  "sxyprn.com/lesbian.html",  "noodlemagazine.com/video/lesbian",  "ashemaletube.com",  "x-tg.tube",  "trannytube.tv",  "obutsumania.com",  "thisvid.com/categories/scat",  "scat.gold",  "motherless.com/term/scat",  "xpee.com","eropuru.com",  "bi-girl.net",  "gazounabi.com",  "intervalues.com/idol.html",  "gurasen.com",  "pictoa.com",  "aznude.com",  "thefappeningblog.com",  "celebjihad.com/main6",  "socialmediagirls.com",  "celeb.gate.cc",  "bannedsextapes.com/tube_tour2/index.html",  "cfake.com/home",  "adultdeepfakes.com",  "realdeepfakes.com",  "deepfakeporn.net",  "sexcelebrity.net","hostlove.com",  "bbs.mikocon.com/forum.php",  "oshioki24.com",  "planetsuzy.org",  "pornbb.org/forum",  "forums.socialmediagirls.com",  "f95zone.to",  "forum.phun.org",  "titsintops.com/phpBB2",  "vintage-erotica-forum.com",  "efukt.com",  "inhumanity.com",  "humoron.com",  "9gag.com/nsfw",  "daftporn.com",  "h-taikendan.net",  "h-ken.net",  "kanno-novel.jp",  "incest-story.com",  "chyoa.com",  "lushstories.com",  "adult-machiko.com",  "sugirl.info",  "milk-key.com",  "sukebei.nyaa.si",  "ffjav.com",  "ggbases.com",  "1337x.to/popular-xxx",  "xxxclub.to",  "joylovedolls.com",  "yourdoll.com",  "mygaysites.com",  "pornwebmasters.com",  "porndude2.com",  "theporndude.vip",  "porngeek.com",  "pornwebmasters.com",  "porndudecasting.com",  "x.com/porndudecasting",  "porndudecams.com",  "porndudecasting.com",  "x.com/porndudecasting",  "porndudeshop.com",  "porndudedeutsch.com"]


#  ==========================================
#  フォルダロック用クラス

#  ==========================================
class  FolderLocker:
        def  __init__(self):
                #  フォルダ内にロック用の空ファイルを作る
                self.lock_path  =  os.path.join(BASE_DIR,  "system.lock")
                self.file_handle  =  None
                self.lock()

        def  lock(self):
                try:
                        #  ファイルを書き込みモードで開き、閉じずに保持し続ける
                        self.file_handle  =  open(self.lock_path,  "w")
                        self.file_handle.write("LOCKED")
                        self.file_handle.flush()

                        #  隠しファイル属性を付与して目立たなくする
                        subprocess.run(["attrib",  "+h",  self.lock_path],  creationflags=0x08000000)
                except:
                        pass

#  ==========================================
#  データ管理クラス
#  ==========================================
class  UsageManager:
        def  __init__(self):
                self.filepath  =  os.path.join(os.path.dirname(os.path.abspath(__file__)),  JSON_FILE)
                #  改ざん防止用の秘密のキー（この文字列は外部から推測されにくいものにするとより安全）
                self.secret_key  =  "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
                self.data  =  self.load_data()

        def  _calculate_checksum(self,  encoded_data_str):
                """エンコードされたデータ文字列からチェックサムを計算する"""
                return  hashlib.sha256((encoded_data_str  +  self.secret_key).encode('utf-8')).hexdigest()

        def  load_data(self):
                today_str  =  datetime.date.today().isoformat()
                default_data  =  {"date":  today_str,  "usage":  {k:  0  for  k  in  TIME_LIMITS}}

                def  reset_and_save():
                        """データをデフォルトにリセットし、安全な形式で保存する"""
                        self.data  =  default_data
                        self.save_data()  #  新しいsave_dataを呼び出す
                        return  default_data

                if  not  os.path.exists(self.filepath):
                        return  reset_and_save()

                try:
                        with  open(self.filepath,  'r')  as  f:
                                saved_content  =  json.load(f)

                        #  1.  構造チェック
                        if  "data"  not  in  saved_content  or  "checksum"  not  in  saved_content:
                                return  reset_and_save()  #  不正な形式

                        encoded_data  =  saved_content["data"]
                        saved_checksum  =  saved_content["checksum"]

                        #  2.  改ざんチェック
                        if  self._calculate_checksum(encoded_data)  !=  saved_checksum:
                                return  reset_and_save()  #  チェックサム不一致（改ざん）

                        #  3.  デコードとデータ復元
                        decoded_json_str  =  base64.b64decode(encoded_data.encode('utf-8')).decode('utf-8')
                        data  =  json.loads(decoded_json_str)

                        #  4.  日付チェック
                        if  data.get("date")  !=  today_str:
                                return  reset_and_save()  #  日付が古い

                        return  data
                except:
                        #  JSONデコードエラー、Base64デコードエラーなど、あらゆる例外をキャッチ
                        return  reset_and_save()

        def  save_data(self):
                try:
                        #  1.  データをJSON文字列に変換
                        json_str  =  json.dumps(self.data)
                        #  2.  Base64でエンコード
                        encoded_data  =  base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
                        #  3.  チェックサムを計算
                        checksum  =  self._calculate_checksum(encoded_data)

                        #  4.  保存するデータ構造を作成
                        content_to_save  =  {
                                "data":  encoded_data,
                                "checksum":  checksum
                        }

                        #  5.  ファイルに書き込み
                        with  open(self.filepath,  'w')  as  f:
                                json.dump(content_to_save,  f)
                                f.flush()
                                os.fsync(f.fileno())  #  ディスクへの書き込みを強制
                except:
                        pass

        def  add_usage(self,  domain,  seconds):
                today_str  =  datetime.date.today().isoformat()
                #  起動中に日付が変わった場合の処理
                if  self.data["date"]  !=  today_str:
                        self.data  =  {"date":  today_str,  "usage":  {k:  0  for  k  in  TIME_LIMITS}}
                        #  この後のsave_data()でリセットされたデータが保存される

                if  domain  not  in  self.data["usage"]:
                        self.data["usage"][domain]  =  0

                self.data["usage"][domain]  +=  seconds
                self.save_data()

        def  get_usage(self,  domain):
                return  int(self.data["usage"].get(domain,  0))

#  ==========================================
#  GUIクラス  (リサイズ対応版)
#  ==========================================
class OverlayApp:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager

        self.root.title("Time Keeper")
        self.root.geometry("280x450+50+50")
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.root.resizable(True, True)
        self.root.minsize(250, 400)

        # Main Scrollable Frame (to handle dynamic content better)
        self.main_scroll = ctk.CTkScrollableFrame(root, fg_color="transparent", scrollbar_button_color=("#f0f2f5", "#242424"), scrollbar_button_hover_color=("#f0f2f5", "#242424"))
        self.main_scroll.pack(side='top', fill='both', expand=True, padx=10, pady=5)

        # Header
        header = ctk.CTkLabel(self.main_scroll, text="⏳ 本日の使用状況", font=ctk.CTkFont(family="Meiryo UI", size=16, weight="bold"))
        header.pack(anchor='w', pady=(5, 10))

        # Cards Container
        self.progress_bars = {}
        self.time_labels = {}
        
        for domain in TIME_LIMITS:
            self.create_domain_card(self.main_scroll, domain)

        # Separator
        separator = ctk.CTkFrame(self.main_scroll, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill='x', pady=15)

        # Block List Toggle
        self.is_blocklist_open = False
        block_toggle_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        block_toggle_frame.pack(fill='x', pady=2)
        
        self.toggle_btn = ctk.CTkButton(block_toggle_frame, text="▶ 表示", width=50, height=24, fg_color="#333333", hover_color="#555555", font=ctk.CTkFont(size=11), command=self.toggle_block_list)
        self.toggle_btn.pack(side='left')
        ctk.CTkLabel(block_toggle_frame, text=f" 完全ブロックリスト ({len(BLOCK_LIST)}件)", font=ctk.CTkFont(family="Meiryo UI", size=11, weight="bold")).pack(side='left', padx=5)

        self.block_list_frame = ctk.CTkScrollableFrame(self.main_scroll, height=100, fg_color=("#e9ecef", "#2b2b2b"), corner_radius=8, scrollbar_button_color=("#e9ecef", "#2b2b2b"), scrollbar_button_hover_color=("#e9ecef", "#2b2b2b"))
        for item in BLOCK_LIST:
            ctk.CTkLabel(self.block_list_frame, text=f"• {item}", font=ctk.CTkFont(family="Consolas", size=11)).pack(anchor='w', padx=5, pady=1)

        # White List Toggle
        self.is_whitelist_open = False
        wl_toggle_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        wl_toggle_frame.pack(fill='x', pady=(10, 2))

        self.wl_toggle_btn = ctk.CTkButton(wl_toggle_frame, text="▶ 表示", width=50, height=24, fg_color="#333333", hover_color="#555555", font=ctk.CTkFont(size=11), command=self.toggle_white_list)
        self.wl_toggle_btn.pack(side='left')
        ctk.CTkLabel(wl_toggle_frame, text=f" 許可リスト ({len(WHITE_LIST)}件)", font=ctk.CTkFont(family="Meiryo UI", size=11, weight="bold")).pack(side='left', padx=5)

        self.white_list_frame = ctk.CTkScrollableFrame(self.main_scroll, height=100, fg_color=("#e9ecef", "#2b2b2b"), corner_radius=8, scrollbar_button_color=("#e9ecef", "#2b2b2b"), scrollbar_button_hover_color=("#e9ecef", "#2b2b2b"))
        for item in WHITE_LIST:
            ctk.CTkLabel(self.white_list_frame, text=f"✓ {item}", font=ctk.CTkFont(family="Consolas", size=11), text_color="#198754").pack(anchor='w', padx=5, pady=1)

        # Status Bar
        self.status_var = ctk.StringVar(value="システム稼働中...")
        self.status_frame = ctk.CTkFrame(root, height=35, fg_color="#1f538d", corner_radius=0)
        self.status_frame.pack(side='bottom', fill='x')
        self.status_frame.pack_propagate(False)
        self.status_label = ctk.CTkLabel(self.status_frame, textvariable=self.status_var, font=ctk.CTkFont(family="Meiryo UI", size=11, weight="bold"), text_color="white")
        self.status_label.pack(expand=True)

        self.update_gui()

    def create_domain_card(self, parent, domain):
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("white", "#2b2b2b"), border_width=1, border_color=("gray85", "gray25"))
        card.pack(fill='x', pady=5, padx=2)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill='x', padx=10, pady=(8, 5))

        domain_lbl = ctk.CTkLabel(top_row, text=domain, font=ctk.CTkFont(family="Meiryo UI", size=12, weight="bold"))
        domain_lbl.pack(side='left')

        time_lbl = ctk.CTkLabel(top_row, text="--:--", font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), text_color="gray")
        time_lbl.pack(side='right')
        self.time_labels[domain] = time_lbl

        pb = ctk.CTkProgressBar(card, height=6, corner_radius=3, progress_color="#1f538d")
        pb.pack(fill='x', padx=10, pady=(0, 8))
        pb.set(0)
        self.progress_bars[domain] = pb

    def toggle_block_list(self):
        if self.is_blocklist_open:
            self.block_list_frame.pack_forget()
            self.toggle_btn.configure(text="▶ 表示")
        else:
            self.block_list_frame.pack(fill='x', pady=10, padx=5)
            self.toggle_btn.configure(text="▼ 隠す")
        self.is_blocklist_open = not self.is_blocklist_open

    def toggle_white_list(self):
        if self.is_whitelist_open:
            self.white_list_frame.pack_forget()
            self.wl_toggle_btn.configure(text="▶ 表示")
        else:
            self.white_list_frame.pack(fill='x', pady=10, padx=5)
            self.wl_toggle_btn.configure(text="▼ 隠す")
        self.is_whitelist_open = not self.is_whitelist_open

    def disable_event(self):
        pass

    def update_gui(self):
        today_str = datetime.date.today().isoformat()
        if self.manager.data["date"] != today_str:
            self.manager.data = {"date": today_str, "usage": {k: 0 for k in TIME_LIMITS}}
            self.manager.save_data()

        for domain, limit in TIME_LIMITS.items():
            used = self.manager.get_usage(domain)
            remaining = max(0, limit - used)
            rem_min = remaining // 60
            rem_sec = remaining % 60

            pb = self.progress_bars[domain]
            # Progress bar set uses 0.0 to 1.0
            fraction = min(1.0, used / limit) if limit > 0 else 1.0
            pb.set(fraction)
            
            lbl = self.time_labels[domain]
            if used >= limit:
                lbl.configure(text="Time Up", text_color="#ff4a4a")
                pb.configure(progress_color="#ff4a4a")
            else:
                lbl.configure(text=f"{rem_min:02}:{rem_sec:02}", text_color=("#1f538d", "#5da2ed"))
                if fraction > 0.8:
                    pb.configure(progress_color="#e6a23c") # Warning color near limit
                else:
                    pb.configure(progress_color="#1f538d")

        self.root.after(1000, self.update_gui)

    def set_status(self, text):
        self.status_var.set(text)
        if "BLOCKED" in text or "TIME UP" in text:
            self.status_frame.configure(fg_color="#ff4a4a")
        elif "Counting" in text:
            self.status_frame.configure(fg_color="#e6a23c")
        elif "Allowed" in text:
            self.status_frame.configure(fg_color="#4caf50")
        else:
            self.status_frame.configure(fg_color="#1f538d")

#  ==========================================
#  監視ロジック
#  ==========================================
def  watchdog_thread():
        """他のすべての監視プロセスが生きているか0.2秒ごとに一括チェックする専用スレッド"""
        while  True:
                try:
                        ensure_processes_running()
                except:
                        pass
                time.sleep(0.2)

def  perform_block(window):
      try:
            if  "Chrome_WidgetWin_1"  in  window.ClassName:
                  #  裏にあるウィンドウを操作する場合、フォーカスを当てないとキー送信が誤爆するため
                  window.SetFocus()
                  #  アドレスバーの探索・書き換え処理を削除し、直接Ctrl+Wを送信してタブを閉じる
                  window.SendKeys('{Ctrl}w')
      except:
            pass

def  monitor_thread(app,  manager):
        last_check_time = time.time()
        url_cache = {}
        while  True:
                try:
                        now = time.time()
                        elapsed_seconds = now - last_check_time
                        last_check_time = now

                        #  全てのトップレベルウィンドウを取得
                        root  =  auto.GetRootControl()
                        children  =  root.GetChildren()

                        status_priority  =  0  #  0:Idle,  1:Safe,  2:Counting,  3:TimeUp,  4:Blocked
                        status_text  =  "💤  Idle"

                        #  このループサイクルですでにカウントしたドメインを記録（複数窓での倍速カウント防止）
                        counted_domains  =  set()

                        for  window  in  children:
                                #  ブラウザ以外はスキップ（負荷軽減）
                                if  "Chrome_WidgetWin_1"  not  in  window.ClassName:
                                        continue

                                hwnd = window.NativeWindowHandle
                                current_url  =  ""
                                
                                # 1. 高速なショートカットキーでの検索
                                edit = auto.EditControl(searchFromControl=window, AccessKey="Ctrl+L")
                                if edit.Exists(0, 0):
                                        try:
                                                current_url = edit.GetValuePattern().Value
                                                url_cache[hwnd] = current_url
                                        except:
                                                pass
                                else:
                                        # 2. 従来の名前での検索
                                        edit = window.Control(ControlType=auto.ControlType.EditControl, Name="アドレスと検索バー", searchDepth=4)
                                        if not edit.Exists(0, 0):
                                                edit = window.Control(ControlType=auto.ControlType.EditControl, Name="Address and search bar", searchDepth=4)
                                        if not edit.Exists(0, 0):
                                                edit  =  window.EditControl()
                                        
                                        if  edit.Exists(0,  0):
                                                try:
                                                        current_url  =  edit.GetValuePattern().Value
                                                        url_cache[hwnd] = current_url
                                                except:
                                                        pass
                                
                                # 取得失敗時はキャッシュを利用
                                if not current_url:
                                        current_url = url_cache.get(hwnd, "")

                                if  not  current_url:
                                        continue

                                url_base  =  current_url.split('?')[0]

                                #  0.  ホワイトリスト
                                whitelisted_word  =  next((word  for  word  in  WHITE_LIST  if  word  in  url_base),  None)
                                if  whitelisted_word:
                                        if  status_priority  <  1:
                                                status_text  =  f"🛡️  Allowed:  {whitelisted_word}"
                                                status_priority  =  1
                                        continue

                                #  1.  即時ブロック
                                blocked_word  =  next((word  for  word  in  BLOCK_LIST  if  word  in  url_base),  None)
                                if  blocked_word:
                                        status_text  =  f"🚫  BLOCKED:  {blocked_word}"
                                        status_priority  =  4
                                        perform_block(window)
                                        continue

                                #  2.  時間制限
                                limited_domain  =  next((d  for  d  in  TIME_LIMITS  if  d  in  current_url),  None)
                                if  limited_domain:
                                        #  まだこのサイクルでカウントしていない場合のみ加算
                                        if  limited_domain  not  in  counted_domains:
                                                manager.add_usage(limited_domain,  elapsed_seconds)
                                                counted_domains.add(limited_domain)

                                        used  =  manager.get_usage(limited_domain)
                                        limit  =  TIME_LIMITS[limited_domain]

                                        if  used  >=  limit:
                                                status_text  =  f"⌛  TIME  UP:  {limited_domain}"
                                                status_priority  =  3
                                                perform_block(window)
                                        else:
                                                if  status_priority  <  2:
                                                        status_text  =  f"⏱  Counting:  {limited_domain}"
                                                        status_priority  =  2
                                else:
                                        if  status_priority  <  1:
                                                status_text  =  "✅  Safe  Browsing"
                                                status_priority  =  1

                        app.set_status(status_text)

                except  Exception:
                        pass

                time.sleep(1.0)

#  ==========================================
#  ヘルパー関数
#  ==========================================
TH32CS_SNAPPROCESS = 2

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260)
    ]

def get_running_exes():
    kernel32 = ctypes.windll.kernel32
    CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
    Process32First = kernel32.Process32First
    Process32Next = kernel32.Process32Next
    CloseHandle = kernel32.CloseHandle

    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if hProcessSnap == -1:
        return set()

    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
    
    exes = set()
    if Process32First(hProcessSnap, ctypes.byref(pe32)):
        while True:
            try:
                exe_name = pe32.szExeFile.decode('mbcs').lower()
                exes.add(exe_name)
            except:
                pass
            if not Process32Next(hProcessSnap, ctypes.byref(pe32)):
                break
    CloseHandle(hProcessSnap)
    return exes

def ensure_processes_running():
        try:
                exes = get_running_exes()
                
                for script_name, exe_name in TARGETS:
                        if script_name == MY_FILENAME:
                                continue
                        
                        exe_basename = os.path.basename(exe_name)
                        if exe_basename.lower() not in exes:
                                script_path = os.path.join(BASE_DIR, script_name)
                                if script_name.endswith('.exe'):
                                        subprocess.Popen([exe_name], creationflags=0x08000000, cwd=BASE_DIR)
                                else:
                                        subprocess.Popen([exe_name, script_path], creationflags=0x08000000, cwd=BASE_DIR)
        except:
                pass

#  ==========================================
#  メイン  (エラーログ機能付き)
#  ==========================================
def  main():
        ERROR_ALREADY_EXISTS = 183
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "URLBlocker_Exe_Mutex_07")
        if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
                return

        #  フォルダをロックして名前変更を防ぐ
        locker  =  FolderLocker()

        manager  =  UsageManager()
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        root  =  ctk.CTk()
        app  =  OverlayApp(root,  manager)


        t  =  threading.Thread(target=monitor_thread,  args=(app,  manager),  daemon=True)
        t.start()

        #  監視.pywを見張る専用スレッドを起動
        t_watch  =  threading.Thread(target=watchdog_thread,  daemon=True)
        t_watch.start()

        root.mainloop()

if  __name__  ==  "__main__":
        try:
                main()
        except  Exception  as  e:
                import  traceback
                with  open(os.path.join(os.path.dirname(os.path.abspath(__file__)),  "error_log.txt"),  "w")  as  f:
                        f.write(traceback.format_exc())
