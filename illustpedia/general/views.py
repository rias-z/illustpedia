from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.views import generic
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import IPUser, Artist, Illust
from taggit.models import Tag
from collections import OrderedDict
from pixivpy3 import *
import time
import copy


# Form
class AccountCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = IPUser
        fields = ("username", "nickname", "email")


class ArtistCreateForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ("artist_id", "artist_name", "tags", "thumbnail")


class TagSearchForm(forms.Form):
    tag_list = forms.CharField(label="検索タグ", max_length=100)


class ArtistUpdateForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ("artist_id", "artist_name", "tags", "thumbnail")


class IllustRegisterForm(forms.ModelForm):
    class Meta:
        model = Illust
        fields = ("image", "tags")


class IllustTagSearchForm(forms.Form):
    tag_list = forms.CharField(label="検索タグ", max_length=100)


# View
class IndexView(generic.TemplateView):
    template_name = 'I000_home.html'


class LoginView(generic.FormView):
    template_name = 'I001_login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('general:top')

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        login(user=user, request=self.request)
        return super(LoginView, self).form_valid(form)


class LogoutView(generic.View):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return redirect('general:home')


class AccountCreateView(generic.CreateView):
    template_name = 'I002_account_create.html'
    form_class = AccountCreateForm
    success_url = reverse_lazy('general:top')

    def done(self, request, cleaned_data):
        obj = AccountCreateForm(request.POST).save(commit=False)
        obj.created_by = self.request.user
        obj.save()

        # ユーザを作成してログイン処理し、トップに遷移する　一時退避
        # user = authenticate(username=cleaned_data['username'],
        #                     password=cleaned_data['password1'])
        # login(self.request, user)
        # return redirect(reverse('general:top', args=(), kwargs={}))

    def get_success_url(self):
            return reverse_lazy('general:login')


class TopView(generic.FormView):
    template_name = 'I003_top.html'
    form_class = TagSearchForm
    tag_list = None

    def get_context_data(self, **kwargs):
        context = super(TopView, self).get_context_data(**kwargs)

        # あなたへのおすすめ一覧（フォローしていない作者１０人）
        dict_tag_and_count_list = {}
        user_follow_artist_list = self.request.user.fav_artist.all()

        # 自分のフォローしている作者のタグを総計する
        for artist in user_follow_artist_list:
            all_artist_tag = artist.tags.all()
            for tag in all_artist_tag:
                if tag in dict_tag_and_count_list.keys():
                    dict_tag_and_count_list[tag] += 1
                else:
                    dict_tag_and_count_list.update({tag: 1})

        # 総計したタグの辞書を、タグの数が多い順に降順リストに変更する
        dict_sort_tag_list_order = OrderedDict(
            sorted(dict_tag_and_count_list.items(), key=lambda x: x[1], reverse=True))

        # リストを上位５番目までカットしたリスト
        dict_sort_tag_list_order_keys = list(dict_sort_tag_list_order.keys())[:5]

        # 優先作者タグリストからリサーチ
        dict_artist_and_count_list = {}
        for tag in dict_sort_tag_list_order_keys:
            research_tag_artist_list = Artist.objects.filter(tags__name__in=[tag])
            for artist in research_tag_artist_list:
                if artist in dict_artist_and_count_list:
                    dict_artist_and_count_list[artist] += 1
                else:
                    dict_artist_and_count_list.update({artist: 1})

        # 作者を降順にリスト化
        dict_sort_artist_list_order = list(OrderedDict(sorted(dict_artist_and_count_list.items(),
                                                              key=lambda x: x[1], reverse=True)).keys())

        # フォローしていない作者リスト
        dict_sort_artist_list_order_non_follow = copy.deepcopy(dict_sort_artist_list_order)

        for artist in user_follow_artist_list:
            if artist in dict_sort_artist_list_order_non_follow:
                dict_sort_artist_list_order_non_follow.remove(artist)

        context['artist_list'] = Artist.objects.all()
        context['all_tag_list'] = Tag.objects.all()
        context['dict_sort_artist_list_order_non_follow'] = dict_sort_artist_list_order_non_follow[:10]
        return context

    def form_valid(self, form):
        tag_list = form.cleaned_data['tag_list']

        if self.request.method == 'POST':
            if 'button_1' in self.request.POST:
                self.success_url = reverse('general:tag_search', kwargs={'tag_list': tag_list, 'is_all': 0})
            elif 'button_2' in self.request.POST:
                self.success_url = reverse('general:tag_search', kwargs={'tag_list': tag_list, 'is_all': 1})

        return super(TopView, self).form_valid(form)


class AccountView(generic.TemplateView):
    template_name = 'I004_account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context['artist_list'] = self.request.user.fav_artist.all()
        return context


class ArtistCreateView(generic.CreateView):
    template_name = 'I005_artist_create.html'
    form_class = ArtistCreateForm

    def get_success_url(self):
        return reverse_lazy('general:artist_detail', args=[self.object.id])


class ArtistDetailView(generic.DetailView):
    template_name = 'I006_artist_detail.html'
    model = Artist, Tag

    def get_queryset(self):
        self.queryset = Artist.objects.all()
        return super(ArtistDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ArtistDetailView, self).get_context_data(**kwargs)
        context['artist'] = self.get_object()
        context['tag_list'] = self.get_object().tags.all()
        flag_fav = False
        if self.request.user.fav_artist.all().filter(artist_id=self.get_object().artist_id):
            flag_fav = True
        context['flag_fav'] = flag_fav
        return context

    def post(self, request, *args, **kwargs):
        artist_list = self.request.user.fav_artist
        artist_list.add(self.get_object())
        return redirect("general:artist_detail", pk=self.kwargs.get("pk"))


class ArtistUpdateView(generic.UpdateView):
    template_name = 'I007_artist_update.html'
    form_class = ArtistUpdateForm
    model = Artist

    def get_queryset(self):
        self.queryset = Artist.objects.all()
        return super(ArtistUpdateView, self).get_queryset()

    def get(self, request, pk, *args, **kwargs):
        return super(ArtistUpdateView, self).get(request)

    def get_success_url(self):
        return reverse_lazy('general:artist_detail', args=[self.object.id])


class TagSearchView(generic.TemplateView):
    template_name = 'I008_tag_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super(TagSearchView, self).get_context_data(**kwargs)
        tag_list = kwargs.get('tag_list').split(',')
        is_all = kwargs.get('is_all')

        hit_tag_artist_list = []

        # ユーザのフォローしている作者
        user_follow_artist_list = self.request.user.fav_artist.all()

        # 検索タグにヒットした作者のリスト
        for tag in tag_list:
            list_hit_artist = Artist.objects.filter(tags__name__in=[tag])
            hit_tag_artist_list.extend(list_hit_artist)

        hit_tag_artist_list = list(set(hit_tag_artist_list))

        # タグとタグ数の辞書
        dict_tag_and_count_list = {}

        # ユーザのフォローしている作者すべてから、タグを抽出
        for artist in user_follow_artist_list:
            all_artist_tag = artist.tags.all()
            for tag in all_artist_tag:
                if tag in dict_tag_and_count_list.keys():
                    dict_tag_and_count_list[tag] += 1
                else:
                    dict_tag_and_count_list.update({tag: 1})

        # タグを多い順にソートして5つだけにした辞書（優先作者タグ）
        dict_sort_tag_list = sorted(dict_tag_and_count_list.items(), key=lambda x: x[1], reverse=True)
        dict_sort_tag_list_order = OrderedDict(sorted(dict_tag_and_count_list.items(), key=lambda x: x[1], reverse=True))

        # ソートされたタグのリスト（優先作者タグリスト）
        dict_sort_tag_list_order_keys = list(dict_sort_tag_list_order.keys())[:5]

        # # 優先作者タグリストからリサーチ
        dict_artist_and_count_list = {}
        for tag in dict_sort_tag_list_order_keys:
            # （優先作者タグ）&&（検索タグにヒットした作者のリスト）
            # research_tag_artist_list = Artist.objects.filter(tags__name__in=[tag])
            # research_tag_artist_list = hit_tag_artist_list.filter(tags__name__in=[tag])

            for artist in hit_tag_artist_list:
                if tag in artist.tags.all():
                    if artist in dict_artist_and_count_list:
                        dict_artist_and_count_list[artist] += 1
                    else:
                        dict_artist_and_count_list.update({artist: 1})

            # for artist in research_tag_artist_list:
            #     if artist in dict_artist_and_count_list:
            #         dict_artist_and_count_list[artist] += 1
            #     else:
            #         dict_artist_and_count_list.update({artist: 1})

        # すべて検索
        if is_all == "0":
            dict_sort_artist_list_order = hit_tag_artist_list

        # 推薦検索
        elif is_all == "1":
            # 作者を降順にリスト化
            dict_sort_artist_list_order = list(OrderedDict(sorted(dict_artist_and_count_list.items(),
                                                                  key=lambda x: x[1], reverse=True)).keys())

        # フォローしていない作者リスト
        dict_sort_artist_list_order_non_follow = copy.deepcopy(dict_sort_artist_list_order)
        for artist in user_follow_artist_list:
            if artist in dict_sort_artist_list_order_non_follow:
                dict_sort_artist_list_order_non_follow.remove(artist)

        context['hit_tag_artist_list'] = hit_tag_artist_list
        context['dict_sort_tag_list_order'] = list(dict_sort_tag_list)[:5]
        context['user_follow_artist_list'] = user_follow_artist_list
        context['dict_sort_artist_list_order'] = dict_sort_artist_list_order
        context['dict_sort_artist_list_order_non_follow'] = dict_sort_artist_list_order_non_follow
        return context


class TagSearchFromArtistView(generic.TemplateView):
    template_name = 'I008_tag_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super(TagSearchFromArtistView, self).get_context_data(**kwargs)
        tag_num = kwargs.get('tag_num')

        # # 検索タグにヒットした作者のリスト
        hit_tag_artist_list = Artist.objects.filter(tags__id__in=[tag_num])

        # タグとタグ数の辞書
        dict_tag_and_count_list = {}

        # ユーザのフォローしている作者
        user_follow_artist_list = self.request.user.fav_artist.all()

        # ユーザのフォローしている作者すべてから、タグを抽出
        for artist in user_follow_artist_list:
            all_artist_tag = artist.tags.all()
            for tag in all_artist_tag:
                if tag in dict_tag_and_count_list.keys():
                    dict_tag_and_count_list[tag] += 1
                else:
                    dict_tag_and_count_list.update({tag: 1})

        # タグを多い順にソートして5つだけにした辞書（優先作者タグ）
        dict_sort_tag_list = sorted(dict_tag_and_count_list.items(), key=lambda x: x[1], reverse=True)
        dict_sort_tag_list_order = OrderedDict(
            sorted(dict_tag_and_count_list.items(), key=lambda x: x[1], reverse=True))

        # ソートされたタグのリスト（優先作者タグリスト）
        dict_sort_tag_list_order_keys = list(dict_sort_tag_list_order.keys())[:5]

        # 優先作者タグリストからリサーチ
        dict_artist_and_count_list = {}
        for tag in dict_sort_tag_list_order_keys:
            # （優先作者タグ）&&（検索タグにヒットした作者のリスト）
            # research_tag_artist_list = Artist.objects.filter(tags__name__in=[tag])
            research_tag_artist_list = hit_tag_artist_list.filter(tags__name__in=[tag])
            for artist in research_tag_artist_list:
                if artist in dict_artist_and_count_list:
                    dict_artist_and_count_list[artist] += 1
                else:
                    dict_artist_and_count_list.update({artist: 1})

        # 作者を降順にリスト化
        dict_sort_artist_list_order = list(OrderedDict(sorted(dict_artist_and_count_list.items(),
                                                              key=lambda x: x[1], reverse=True)).keys())

        # フォローしていない作者リスト
        dict_sort_artist_list_order_non_follow = copy.deepcopy(dict_sort_artist_list_order)
        for artist in user_follow_artist_list:
            if artist in dict_sort_artist_list_order_non_follow:
                dict_sort_artist_list_order_non_follow.remove(artist)

        context['hit_tag_artist_list'] = hit_tag_artist_list
        context['dict_sort_tag_list_order'] = list(dict_sort_tag_list)[:5]
        context['user_follow_artist_list'] = user_follow_artist_list
        context['dict_sort_artist_list_order'] = dict_sort_artist_list_order
        context['dict_sort_artist_list_order_non_follow'] = dict_sort_artist_list_order_non_follow
        return context


class ArtistAutoCreateFromRankingView(generic.TemplateView):
    template_name = 'I009_create_from_ranking.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ArtistAutoCreateFromRankingView, self).get_context_data(**kwargs)

        # ログイン処理
        api = PixivAPI()
        api.login('sabureb0y@gmail.com', 'k0k0beanPedia')

        artist_list = []        # ランキングのすべての作者リスト
        list_all_id = []        # illustpediaに登録されているすべての作者idのリスト
        new_artist_list = []    # 新規作成された作者のリスト

        for artist in Artist.objects.all():
            list_all_id.append(artist.artist_id)

        # pixivのデイリーランキングのjsonをクローラ
        json_result = api.ranking_all('daily')
        ranking = json_result.response[0]
        for artist in ranking.works:
            print("<%s>[%s] %s" % (artist.rank, artist.work.user.id, artist.work.user.name))
            artist_list.append([artist.rank, artist.work.user.id, artist.work.user.name])

        count = 0
        for artist in artist_list:
            flag_exist = False
            for artist_id in list_all_id:

                # 作者がすでに登録されている場合
                if artist[1] == artist_id:
                    flag_exist = True
                    break

            # 作者が登録されていない場合
            if not flag_exist:
                print("4 minutes wait...\n")
                time.sleep(4)
                print("[" + artist[2] + "]のページを作成中")

                # それぞれのartistのページから、イラスト30個分のタグを数の多い順にソート、上位５つを仮作者タグにする
                dict_tag = {}
                json_artist_result = api.users_works(artist[1]).response
                for illust in json_artist_result:
                    for tag in illust.tags:
                        if 'users' not in tag:
                            if tag in dict_tag.keys():
                                dict_tag[tag] += 1
                            else:
                                dict_tag.update({tag: 1})
                dict_sort_tag = list(OrderedDict(sorted(dict_tag.items(), key=lambda x: x[1], reverse=True)).keys())[:5]

                # 新規作成された作者リストに追加
                new_artist = Artist.objects.create(artist_id=artist[1], artist_name=artist[2])
                for tag in dict_sort_tag:
                    new_artist.tags.add(tag)

                # no_imageとして保存
                new_artist.thumbnail = "./no_image.png"

                # DBに作者を保存
                new_artist.save()

                # 新規作成作者のリストに追加
                new_artist_list.append(new_artist)
                print("NewCreate ==> <%s>[%s] %s" % (str(artist[0]), str(artist[1]), str(artist[2])))
                print("作成完了\n")
                count += 1

            # 追加人数が5人になったら処理を終了する
            if count == 5:
                print("break")
                break

        context['new_artist_list'] = new_artist_list
        return context


class ArtistAutoCreateFromFollowView(generic.TemplateView):
    template_name = 'I010_create_from_pixivFollow.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ArtistAutoCreateFromFollowView, self).get_context_data(**kwargs)

        list_all_follow_artist = []  # すべての作者リスト
        list_all_id = []  # illustpediaに登録されているすべての作者idのリスト
        new_artist_list = []  # 新規作成された作者のリスト

        for artist in Artist.objects.all():
            list_all_id.append(artist.artist_id)

        # ログイン処理
        api = PixivAPI()
        api.login('sabureb0y@gmail.com', 'k0k0beanPedia')

        json_result = api.me_following().response

        for artist in json_result:
            print("[%s] %s" % (artist.id, artist.name))
            list_all_follow_artist.append([artist.id, artist.name])

        count = 0
        for artist in list_all_follow_artist:
            flag_exist = False
            for artist_id in list_all_id:

                # 作者がすでに登録されている場合
                if artist[0] == artist_id:
                    flag_exist = True
                    break

            # 作者が登録されていない場合
            if not flag_exist:
                print("4 minutes wait...\n")
                time.sleep(4)
                print("[" + artist[1] + "]のページを作成中")

                # それぞれのartistのページから、イラスト30個分のタグを数の多い順にソート、上位５つを仮作者タグにする
                dict_tag = {}
                json_artist_result = api.users_works(artist[0]).response
                for illust in json_artist_result:
                    for tag in illust.tags:
                        if 'users' not in tag:
                            if tag in dict_tag.keys():
                                dict_tag[tag] += 1
                            else:
                                dict_tag.update({tag: 1})
                dict_sort_tag = list(OrderedDict(sorted(dict_tag.items(), key=lambda x: x[1], reverse=True)).keys())[:5]

                # 新規作成された作者リストに追加
                new_artist = Artist.objects.create(artist_id=artist[0], artist_name=artist[1])
                for tag in dict_sort_tag:
                    new_artist.tags.add(tag)

                # no_imageとして保存
                new_artist.thumbnail = "./no_image.png"

                # DBに作者を保存
                new_artist.save()

                # 新規作成作者のリストに追加
                new_artist_list.append(new_artist)
                print("NewCreate ==> [%s] %s" % (str(artist[0]), str(artist[1])))
                print("作成完了\n")
                count += 1

            # 追加人数が5人になったら処理を終了する
            if count == 5:
                print("break")
                break

        context['new_artist_list'] = new_artist_list
        return context


class AllArtistView(generic.TemplateView):
    template_name = 'I011_all_artist.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AllArtistView, self).get_context_data(**kwargs)

        context['artist_list'] = Artist.objects.all()
        return context


# イラストDBデータベース
class IllustDBTopView(generic.FormView):
    template_name = 'D001_illust_top.html'
    form_class = IllustTagSearchForm
    tag_list = None
    # success_url = reverse('general:illust_tag_search')

    def get_context_data(self, *args, **kwargs):
        context = super(IllustDBTopView, self).get_context_data(**kwargs)

        context['all_illust_list'] = Illust.objects.all()
        return context

    def form_valid(self, form):
        tag_list = form.cleaned_data['tag_list']
        self.success_url = reverse('general:illust_tag_search', kwargs={'tag_list': tag_list})
        return super(IllustDBTopView, self).form_valid(form)


class IllustDBRegisterView(generic.CreateView):
    template_name = 'D002_illust_register.html'
    form_class = IllustRegisterForm

    def get_success_url(self):
        return reverse_lazy('general:illust_detail', args=[self.object.id])


class IllustDBDetailView(generic.DetailView):
    template_name = 'D003_illust_detail.html'
    model = Illust

    def get_queryset(self):
        self.queryset = Illust.objects.all()
        return super(IllustDBDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(IllustDBDetailView, self).get_context_data(**kwargs)
        context['illust'] = self.get_object()
        context['illust_tag_list'] = self.get_object().tags.all()
        return context

    # def post(self, request, *args, **kwargs):
    #     artist_list = self.request.user.fav_artist
    #     artist_list.add(self.get_object())
    #     return redirect("general:artist_detail", pk=self.kwargs.get("pk"))


class IllustTagSearchView(generic.TemplateView):
    template_name = 'D005_illust_tag_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super(IllustTagSearchView, self).get_context_data(**kwargs)
        tag_list = kwargs.get('tag_list').split(',')

        # 検索タグにヒットした作者のリスト
        for tag in tag_list:
            hit_tag_artist_list = Artist.objects.filter(tags__name__in=[tag])

        # タグとタグ数の辞書
        dict_tag_and_count_list = {}

        # ユーザのフォローしている作者
        user_follow_artist_list = self.request.user.fav_artist.all()

        # ユーザのフォローしている作者すべてから、タグを抽出
        for artist in user_follow_artist_list:
            all_artist_tag = artist.tags.all()
            for tag in all_artist_tag:
                if tag in dict_tag_and_count_list.keys():
                    dict_tag_and_count_list[tag] += 1
                else:
                    dict_tag_and_count_list.update({tag: 1})

        # タグを多い順にソートして5つだけにした辞書（優先作者タグ）
        dict_sort_tag_list = sorted(dict_tag_and_count_list.items(), key=lambda x: x[1], reverse=True)
        dict_sort_tag_list_order = OrderedDict(sorted(dict_tag_and_count_list.items(), key=lambda x: x[1], reverse=True))

        # ソートされたタグのリスト（優先作者タグリスト）
        dict_sort_tag_list_order_keys = list(dict_sort_tag_list_order.keys())[:5]

        # 優先作者タグリストからリサーチ
        dict_artist_and_count_list = {}
        for tag in dict_sort_tag_list_order_keys:
            # （優先作者タグ）&&（検索タグにヒットした作者のリスト）
            # research_tag_artist_list = Artist.objects.filter(tags__name__in=[tag])
            research_tag_artist_list = hit_tag_artist_list.filter(tags__name__in=[tag])
            for artist in research_tag_artist_list:
                if artist in dict_artist_and_count_list:
                    dict_artist_and_count_list[artist] += 1
                else:
                    dict_artist_and_count_list.update({artist: 1})

        # 作者を降順にリスト化
        dict_sort_artist_list_order = list(OrderedDict(sorted(dict_artist_and_count_list.items(),
                                                              key=lambda x: x[1], reverse=True)).keys())

        # フォローしていない作者リスト
        dict_sort_artist_list_order_non_follow = copy.deepcopy(dict_sort_artist_list_order)
        for artist in user_follow_artist_list:
            if artist in dict_sort_artist_list_order_non_follow:
                dict_sort_artist_list_order_non_follow.remove(artist)

        context['hit_tag_artist_list'] = hit_tag_artist_list
        context['dict_sort_tag_list_order'] = list(dict_sort_tag_list)[:5]
        context['user_follow_artist_list'] = user_follow_artist_list
        context['dict_sort_artist_list_order'] = dict_sort_artist_list_order
        context['dict_sort_artist_list_order_non_follow'] = dict_sort_artist_list_order_non_follow
        return context