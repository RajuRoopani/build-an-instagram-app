/** app.js - Instagram Clone. Single IIFE, no duplicates. */
(function () {
  'use strict';

  /* === 1. MOCK DATA === */
  var MOCK_DATA = {
    currentUser: { user_id:'u1', username:'you', display_name:'Your Name',
      profile_picture_url:'https://ui-avatars.com/api/?name=Your+Name&background=e0e0e0&color=555&size=150',
      bio:'Living the moment', follower_count:842, following_count:310 },
    users: [
      { user_id:'u2', username:'alex_wanderer', display_name:'Alex Chen',
        profile_picture_url:'https://ui-avatars.com/api/?name=Alex+Chen&background=ffdde1&color=c0392b&size=56', follower_count:4201 },
      { user_id:'u3', username:'sunsetlens', display_name:'Maya Torres',
        profile_picture_url:'https://ui-avatars.com/api/?name=Maya+Torres&background=d4f1f4&color=1a6b7a&size=56', follower_count:12800 },
      { user_id:'u4', username:'foodie_felix', display_name:'Felix Bauer',
        profile_picture_url:'https://ui-avatars.com/api/?name=Felix+Bauer&background=fff3cd&color=856404&size=56', follower_count:7654 },
      { user_id:'u5', username:'neon_nights', display_name:'Priya Sharma',
        profile_picture_url:'https://ui-avatars.com/api/?name=Priya+Sharma&background=e8d5f5&color=6a1b9a&size=56', follower_count:3310 },
      { user_id:'u6', username:'mountain_mo', display_name:'Morgan Hill',
        profile_picture_url:'https://ui-avatars.com/api/?name=Morgan+Hill&background=d5f5e3&color=1e8449&size=56', follower_count:5500 },
      { user_id:'u7', username:'studio_sab', display_name:'Sabrina Lowe',
        profile_picture_url:'https://ui-avatars.com/api/?name=Sabrina+Lowe&background=fde8d8&color=a04000&size=56', follower_count:9870 },
      { user_id:'u8', username:'coastal_kai', display_name:'Kai Nakamura',
        profile_picture_url:'https://ui-avatars.com/api/?name=Kai+Nakamura&background=d6eaf8&color=1a5276&size=56', follower_count:6200 },
      { user_id:'u9', username:'urban_iris', display_name:'Iris Vance',
        profile_picture_url:'https://ui-avatars.com/api/?name=Iris+Vance&background=f9ebea&color=922b21&size=56', follower_count:2980 }
    ],
    posts: [
      { post_id:'p1',  user_id:'u2', like_count:842,  caption:'Golden hour never gets old #travel',
        content_url:'https://picsum.photos/seed/p1/600/600',  created_at:new Date(Date.now()-2*3600e3).toISOString() },
      { post_id:'p2',  user_id:'u3', like_count:2341, caption:'Caught this at 5am. Worth it.',
        content_url:'https://picsum.photos/seed/p2/600/600',  created_at:new Date(Date.now()-5*3600e3).toISOString() },
      { post_id:'p3',  user_id:'u4', like_count:1105, caption:'Homemade ramen from scratch',
        content_url:'https://picsum.photos/seed/p3/600/600',  created_at:new Date(Date.now()-8*3600e3).toISOString() },
      { post_id:'p4',  user_id:'u5', like_count:678,  caption:'The city never sleeps #neonlights',
        content_url:'https://picsum.photos/seed/p4/600/600',  created_at:new Date(Date.now()-12*3600e3).toISOString() },
      { post_id:'p5',  user_id:'u6', like_count:3200, caption:'Summit reached! #hiking',
        content_url:'https://picsum.photos/seed/p5/600/600',  created_at:new Date(Date.now()-86400e3).toISOString() },
      { post_id:'p6',  user_id:'u7', like_count:1876, caption:'New branding project',
        content_url:'https://picsum.photos/seed/p6/600/600',  created_at:new Date(Date.now()-1.5*86400e3).toISOString() },
      { post_id:'p7',  user_id:'u8', like_count:990,  caption:'Dawn patrol. Perfect conditions.',
        content_url:'https://picsum.photos/seed/p7/600/600',  created_at:new Date(Date.now()-2*86400e3).toISOString() },
      { post_id:'p8',  user_id:'u9', like_count:542,  caption:'Hidden mural on Grand Ave',
        content_url:'https://picsum.photos/seed/p8/600/600',  created_at:new Date(Date.now()-3*86400e3).toISOString() },
      { post_id:'p9',  user_id:'u2', like_count:721,  caption:'Road trip day 3 - Nevada',
        content_url:'https://picsum.photos/seed/p9/600/600',  created_at:new Date(Date.now()-4*86400e3).toISOString() },
      { post_id:'p10', user_id:'u3', like_count:4120, caption:'Long exposure waterfall',
        content_url:'https://picsum.photos/seed/p10/600/600', created_at:new Date(Date.now()-5*86400e3).toISOString() },
      { post_id:'p11', user_id:'u4', like_count:2890, caption:'Tokyo street food haul',
        content_url:'https://picsum.photos/seed/p11/600/600', created_at:new Date(Date.now()-6*86400e3).toISOString() },
      { post_id:'p12', user_id:'u6', like_count:1650, caption:'Wildflower season #pnw',
        content_url:'https://picsum.photos/seed/p12/600/600', created_at:new Date(Date.now()-7*86400e3).toISOString() }
    ],
    comments: {
      p1:[{user_id:'u3',text:'Stunning!'},{user_id:'u6',text:'Where is this?'}],
      p2:[{user_id:'u5',text:'The light is insane'}],
      p3:[{user_id:'u8',text:'Recipe please'},{user_id:'u2',text:'Looks comforting!'}],
      p5:[{user_id:'u2',text:'Which trail?'},{user_id:'u3',text:'Need to do this!'}],
      p6:[{user_id:'u9',text:'Love the typography'}],
      p7:[{user_id:'u6',text:'What a session!'}],
      p10:[{user_id:'u6',text:'Silky water'},{user_id:'u5',text:'Exposure time?'}],
      p11:[{user_id:'u9',text:'Tokyo food is the best'}]
    },
    stories:[
      {user_id:'u2',seen:false},{user_id:'u3',seen:false},{user_id:'u4',seen:true},
      {user_id:'u5',seen:false},{user_id:'u6',seen:true},{user_id:'u7',seen:false},
      {user_id:'u8',seen:true},{user_id:'u9',seen:false}
    ],
    suggestions:['u5','u7','u9']
  };

  /* === 2. STATE === */
  var state = {
    likedPosts:{}, bookmarkedPosts:{}, followedUsers:{}, likeCounts:{},
    storyTimer:null, storyIndex:-1, toastTimer:null, tapTimer:null, lastTapWrap:null
  };
  MOCK_DATA.posts.forEach(function(p){ state.likeCounts[p.post_id]=p.like_count; });
  var _overlay=null, _progBar=null;

  /* === 3. HELPERS === */
  function esc(s){var d=document.createElement('div');d.appendChild(document.createTextNode(s));return d.innerHTML;}
  function timeAgo(iso){
    var s=Math.floor((Date.now()-new Date(iso).getTime())/1000);
    if(s<60) return 'just now'; if(s<3600) return Math.floor(s/60)+'m';
    if(s<86400) return Math.floor(s/3600)+'h'; return Math.floor(s/86400)+'d';
  }
  function userById(id){
    if(id===MOCK_DATA.currentUser.user_id) return MOCK_DATA.currentUser;
    for(var i=0;i<MOCK_DATA.users.length;i++) if(MOCK_DATA.users[i].user_id===id) return MOCK_DATA.users[i];
    return null;
  }
  function commentsFor(pid){return MOCK_DATA.comments[pid]||[];}
  function fmtCount(n){
    if(n>=1e6) return (n/1e6).toFixed(1).replace(/\.0$/,'')+'m';
    if(n>=1e4) return (n/1e3).toFixed(1).replace(/\.0$/,'')+'k';
    if(n>=1e3) return n.toLocaleString(); return ''+n;
  }

  /* === 4. RENDER === */
  function renderStories(){
    var bar=document.getElementById('storiesBar'); if(!bar) return;
    var h='';
    MOCK_DATA.stories.forEach(function(s,i){
      var u=userById(s.user_id); if(!u) return;
      var ring=s.seen?'story-ring story-ring--seen':'story-ring';
      h+='<div class="story-item" data-story-index="'+i+'" role="listitem" tabindex="0">'
        +'<div class="'+ring+'"><img src="'+esc(u.profile_picture_url)+'" alt="'+esc(u.username)+'"></div>'
        +'<span class="story-username">'+esc(u.username)+'</span></div>';
    });
    bar.innerHTML=h;
  }

  function buildPostCard(post){
    var u=userById(post.user_id); if(!u) return '';
    var liked=!!state.likedPosts[post.post_id];
    var bm=!!state.bookmarkedPosts[post.post_id];
    var fol=!!state.followedUsers[post.user_id];
    var cnt=state.likeCounts[post.post_id]||0;
    var cs=commentsFor(post.post_id);
    var likeIco=liked?'&hearts;':'&#9825;';
    var bmIco=bm?'&#128278;':'&#128190;';
    var folBtn='';
    if(post.user_id!==MOCK_DATA.currentUser.user_id){
      folBtn='<button class="follow-btn'+(fol?' following':'')+'" data-action="follow" data-user-id="'+post.user_id+'">'+(fol?'Following':'Follow')+'</button>';
    }
    var cmtHtml='';
    cs.slice(0,2).forEach(function(c){
      var cu=userById(c.user_id);
      cmtHtml+='<p class="post-comment"><strong>'+esc(cu?cu.username:'user')+'</strong> '+esc(c.text)+'</p>';
    });
    if(cs.length>2) cmtHtml+='<p class="view-all-comments">View all '+cs.length+' comments</p>';
    return '<article class="post-card" data-post-id="'+post.post_id+'">'
      +'<header class="post-header">'
      +'<img class="post-avatar" src="'+esc(u.profile_picture_url)+'" alt="">'
      +'<div class="post-user-info"><span class="post-username">'+esc(u.username)+'</span>'
      +'<span class="post-time">'+timeAgo(post.created_at)+'</span></div>'+folBtn+'</header>'
      +'<div class="post-image-wrap" data-post-id="'+post.post_id+'">'
      +'<img class="post-image" src="'+esc(post.content_url)+'" alt="Post by '+esc(u.username)+'" loading="lazy">'
      +'<div class="heart-burst" aria-hidden="true">&#10084;&#65039;</div></div>'
      +'<div class="post-actions"><div class="post-actions-left">'
      +'<button class="action-btn like-btn" data-action="like" data-post-id="'+post.post_id+'" aria-label="Like">'+likeIco+'</button>'
      +'<button class="action-btn comment-focus-btn" data-action="comment-focus" data-post-id="'+post.post_id+'" aria-label="Comment">&#128172;</button>'
      +'</div><button class="action-btn bookmark-btn" data-action="bookmark" data-post-id="'+post.post_id+'" aria-label="Bookmark">'+bmIco+'</button></div>'
      +'<div class="post-likes">'+fmtCount(cnt)+' likes</div>'
      +'<div class="post-caption"><strong>'+esc(u.username)+'</strong> '+esc(post.caption)+'</div>'
      +'<div class="post-comments">'+cmtHtml+'</div>'
      +'<div class="comment-form">'
      +'<textarea class="post-card__comment-input" data-post-id="'+post.post_id+'" placeholder="Add a comment..." maxlength="300" rows="1"></textarea>'
      +'<button class="post-card__comment-send" data-action="send-comment" data-post-id="'+post.post_id+'" disabled>Post</button>'
      +'</div></article>';
  }

  function renderFeed(){
    var f=document.getElementById('postFeed'); if(!f) return;
    var h=''; MOCK_DATA.posts.forEach(function(p){h+=buildPostCard(p);}); f.innerHTML=h;
  }
  function renderPosts(){renderFeed();}

  function renderSidebarProfile(){
    var el=document.getElementById('sidebarProfile'); if(!el) return;
    var cu=MOCK_DATA.currentUser;
    el.innerHTML='<img class="sidebar-avatar" src="'+esc(cu.profile_picture_url)+'" alt="">'
      +'<div class="sidebar-user-info"><span class="sidebar-username">'+esc(cu.username)+'</span>'
      +'<span class="sidebar-name">'+esc(cu.display_name)+'</span></div>';
  }

  function renderSuggestions(){
    var el=document.getElementById('suggestionsList'); if(!el) return;
    var h='';
    MOCK_DATA.suggestions.forEach(function(uid){
      var u=userById(uid); if(!u) return;
      var fol=!!state.followedUsers[uid];
      h+='<div class="suggestion-item">'
        +'<img class="suggestion-avatar" src="'+esc(u.profile_picture_url)+'" alt="">'
        +'<div class="suggestion-info"><span class="suggestion-username">'+esc(u.username)+'</span>'
        +'<span class="suggestion-subtitle">Suggested for you</span></div>'
        +'<button class="follow-btn suggestion-follow'+(fol?' following':'')+'" data-action="follow" data-user-id="'+uid+'">'
        +(fol?'Following':'Follow')+'</button></div>';
    });
    el.innerHTML=h;
  }

  /* === 5. INTERACTION HANDLERS === */
  function toggleLike(pid){
    if(state.likedPosts[pid]){delete state.likedPosts[pid];state.likeCounts[pid]=(state.likeCounts[pid]||1)-1;}
    else{state.likedPosts[pid]=true;state.likeCounts[pid]=(state.likeCounts[pid]||0)+1;}
    renderFeed();
  }
  function triggerHeartBurst(wrap,pid){
    var b=wrap.querySelector('.heart-burst');
    if(b){b.classList.add('active');setTimeout(function(){b.classList.remove('active');},800);}
    if(pid&&!state.likedPosts[pid]) toggleLike(pid);
  }
  function toggleBookmark(pid){
    if(state.bookmarkedPosts[pid]) delete state.bookmarkedPosts[pid]; else state.bookmarkedPosts[pid]=true;
    renderFeed();
  }
  function submitComment(pid,text){
    if(!text||!text.trim()) return;
    if(!MOCK_DATA.comments[pid]) MOCK_DATA.comments[pid]=[];
    MOCK_DATA.comments[pid].push({user_id:MOCK_DATA.currentUser.user_id,text:text.trim()});
    renderFeed();
  }
  function toggleFollow(uid){
    if(state.followedUsers[uid]) delete state.followedUsers[uid]; else state.followedUsers[uid]=true;
    renderFeed(); renderSuggestions();
  }

  /* === 6. STORY HANDLERS === */
  function stopStoryProgress(){if(state.storyTimer){clearTimeout(state.storyTimer);state.storyTimer=null;}}
  function startStoryProgress(){
    stopStoryProgress();
    if(_progBar){
      _progBar.style.transition='none';_progBar.style.width='0%';
      void _progBar.offsetWidth;
      _progBar.style.transition='width 5s linear';_progBar.style.width='100%';
    }
    state.storyTimer=setTimeout(function(){
      var n=state.storyIndex+1;
      if(n<MOCK_DATA.stories.length) openStory(n); else closeStory();
    },5000);
  }
  function openStory(idx){
    if(idx<0||idx>=MOCK_DATA.stories.length) return;
    state.storyIndex=idx;
    var s=MOCK_DATA.stories[idx],u=userById(s.user_id); if(!u) return;
    var ov=_overlay||document.getElementById('storyOverlay'); if(!ov) return;
    var img=document.getElementById('storyImage'),un=document.getElementById('storyUsername'),av=document.getElementById('storyAvatar');
    if(img) img.src='https://picsum.photos/seed/story'+u.user_id+'/400/700';
    if(un) un.textContent=u.username; if(av) av.src=u.profile_picture_url;
    ov.classList.add('active'); document.body.style.overflow='hidden';
    s.seen=true; renderStories(); startStoryProgress();
  }
  function closeStory(){
    var ov=_overlay||document.getElementById('storyOverlay');
    if(ov) ov.classList.remove('active');
    document.body.style.overflow=''; stopStoryProgress(); state.storyIndex=-1;
  }

  /* === 7. NEW POST === */
  function handleNewPost(){
    var cap=prompt("What's on your mind?"); if(!cap||!cap.trim()) return;
    var newId='p'+Date.now();
    var np={post_id:newId,user_id:MOCK_DATA.currentUser.user_id,like_count:0,
      caption:cap.trim(),content_url:'https://picsum.photos/seed/'+newId+'/600/600',
      created_at:new Date().toISOString()};
    MOCK_DATA.posts.unshift(np); state.likeCounts[newId]=0;
    renderFeed(); window.scrollTo({top:0,behavior:'smooth'});
  }

  /* === 8. TOAST === */
  function showNewPostsToast(){
    var t=document.getElementById('newPostsToast'); if(!t) return;
    t.classList.add('visible');
    state.toastTimer=setTimeout(function(){t.classList.remove('visible');state.toastTimer=null;},5000);
  }

  /* === 9. EVENT BINDING & INIT === */
  function bindEvents(){
    var feed=document.getElementById('postFeed');
    var bar=document.getElementById('storiesBar');
    var sidebar=document.querySelector('.sidebar');
    var toast=document.getElementById('newPostsToast');

    if(feed){
      /* Delegated click: like / bookmark / follow / comment-focus / send-comment */
      feed.addEventListener('click',function(e){
        var btn=e.target.closest('[data-action]');
        var action=btn&&btn.dataset.action;
        var postId=btn&&btn.dataset.postId;
        var card=btn&&btn.closest('.post-card');
        var ta,sb;
        switch(action){
          case 'like':       toggleLike(postId); break;
          case 'bookmark':   toggleBookmark(postId); break;
          case 'follow':     toggleFollow(btn.dataset.userId); break;
          case 'comment-focus':
            ta=card&&card.querySelector('.post-card__comment-input');
            if(ta) ta.focus(); break;
          case 'send-comment':
            ta=card&&card.querySelector('.post-card__comment-input');
            sb=card&&card.querySelector('.post-card__comment-send');
            if(ta&&ta.value.trim()){
              submitComment(postId,ta.value);
              ta.value=''; ta.style.height='auto';
              if(sb) sb.disabled=true;
            }
            break;
        }
      });

      /* Double-tap to like with heart burst */
      feed.addEventListener('click',function(e){
        var wrap=e.target.closest('.post-image-wrap'); if(!wrap) return;
        var pid=wrap.dataset.postId; if(!pid) return;
        if(state.tapTimer&&state.lastTapWrap===wrap){
          clearTimeout(state.tapTimer); state.tapTimer=null; state.lastTapWrap=null;
          triggerHeartBurst(wrap,pid);
        } else {
          state.lastTapWrap=wrap;
          state.tapTimer=setTimeout(function(){state.tapTimer=null;state.lastTapWrap=null;},350);
        }
      });

      /* Auto-resize textarea + enable Post button */
      feed.addEventListener('input',function(e){
        var ta=e.target.closest('.post-card__comment-input'); if(!ta) return;
        var card=ta.closest('.post-card');
        var sb=card&&card.querySelector('.post-card__comment-send');
        if(sb) sb.disabled=!ta.value.trim();
        ta.style.height='auto'; ta.style.height=Math.min(ta.scrollHeight,80)+'px';
      });

      /* Enter to submit comment */
      feed.addEventListener('keydown',function(e){
        var ta=e.target.closest('.post-card__comment-input');
        if(!ta||e.key!=='Enter'||e.shiftKey) return;
        e.preventDefault();
        var card=ta.closest('.post-card'),postId=ta.dataset.postId;
        var sb=card&&card.querySelector('.post-card__comment-send');
        if(ta.value.trim()){
          submitComment(postId,ta.value);
          ta.value=''; ta.style.height='auto'; if(sb) sb.disabled=true;
        }
      });
    }

    /* Stories bar */
    if(bar){
      bar.addEventListener('click',function(e){
        var item=e.target.closest('[data-story-index]'); if(!item) return;
        var idx=parseInt(item.dataset.storyIndex,10); if(!isNaN(idx)) openStory(idx);
      });
      bar.addEventListener('keydown',function(e){
        if(e.key!=='Enter'&&e.key!==' ') return;
        var item=e.target.closest('[data-story-index]'); if(!item) return;
        e.preventDefault(); openStory(parseInt(item.dataset.storyIndex,10));
      });
    }

    /* Story overlay close */
    var closeBtn=document.getElementById('storyClose');
    if(closeBtn) closeBtn.addEventListener('click',closeStory);
    if(_overlay){
      _overlay.addEventListener('click',function(e){if(e.target===_overlay) closeStory();});
    }

    /* Keyboard: Esc + arrows for story overlay */
    document.addEventListener('keydown',function(e){
      if(!_overlay||!_overlay.classList.contains('active')) return;
      if(e.key==='Escape')     closeStory();
      if(e.key==='ArrowRight') openStory(state.storyIndex+1);
      if(e.key==='ArrowLeft')  openStory(state.storyIndex-1);
    });

    /* Sidebar follow buttons */
    if(sidebar){
      sidebar.addEventListener('click',function(e){
        var btn=e.target.closest('[data-action="follow"]');
        if(btn) toggleFollow(btn.dataset.userId);
      });
    }

    /* Toast click -> scroll to top */
    if(toast){
      toast.addEventListener('click',function(){
        window.scrollTo({top:0,behavior:'smooth'});
        toast.classList.remove('visible');
        if(state.toastTimer){clearTimeout(state.toastTimer);state.toastTimer=null;}
      });
    }

    /* "New post" nav button */
    var newPostBtn=document.querySelector('.nav-btn[aria-label="New post"]');
    if(newPostBtn) newPostBtn.addEventListener('click',handleNewPost);

    /* "Your story" element (if present) */
    var yourStory=document.getElementById('yourStory');
    if(yourStory) yourStory.addEventListener('click',handleNewPost);
  }

  document.addEventListener('DOMContentLoaded',function(){
    _overlay=document.getElementById('storyOverlay');
    _progBar=document.getElementById('storyProgressBar');
    renderStories();
    renderPosts();
    renderSidebarProfile();
    renderSuggestions();
    bindEvents();
    setTimeout(showNewPostsToast,8000);
  });

}()); /* end IIFE */
