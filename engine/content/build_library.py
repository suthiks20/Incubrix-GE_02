"""Builds content/library_30.json. Copy was drafted with Claude from product_notes.txt and input_1.txt (see README: AI disclosure)."""
import json
LI = ["#ContentCreation", "#ShortFormVideo", "#CreatorTools"]
IG = ["#ContentCreation", "#CreatorTips", "#Reels", "#Repurposing"]
YT = ["#Shorts", "#ContentCreation", "#CreatorTips"]
A = []
def add(id, platform, fmt, pillar, hook, caption, cta, tags, facts=(), beats=None, slides=None):
    A.append(dict(id=id, platform=platform, format=fmt, pillar=pillar, hook=hook, caption=caption, cta=cta,
                  hashtags=tags, facts_used=list(facts), beats=beats or [], slides=slides or []))
P1, P2, P3, P4, P5 = ["The reformatting problem and how to fix it", "The product in action", "Hooks and captions",
                      "Idea-to-published workflow", "Honest tests"]

# ---------- 10 short videos ----------
add("V01","YouTube Shorts","Short video",P1,"One video, three platforms, three shapes",
 "One video does not fit every feed. LinkedIn, Reels and Shorts each reward a different first line and a different frame.",
 "Which platform do you rework first?",YT,beats=["One video. Three platforms.","LinkedIn wants context.","Reels want a fast first line.","Shorts want vertical, under 60 seconds.","Same idea. Three native versions.","Which platform do you rework first?"])
add("V02","Instagram","Short video",P5,"I asked for under 150 words. I got 175.",
 "I tested the LinkedIn Content template. The draft ran long and carried claims with no source. A rewrite by chat fixed it.",
 "Do you check drafts before you post?",IG,["F1","F2","F7"],beats=["I asked a template for a LinkedIn post.","I asked for under 150 words.","The draft ran about 175.","It also had numbers with no source.","I asked for a rewrite by chat.","It followed all three instructions.","Do you check drafts before you post?"])
add("V03","YouTube Shorts","Short video",P5,"My clip came out with black bars on most of the frame",
 "I ran a 2:25 landscape video through Clips. It found a 32-second vertical clip, but roughly 70% of the frame was black bars.",
 "What do you check before you post a clip?",YT,["F4","F5"],beats=["I ran a 2:25 video through Clips.","It found one clip. 32 seconds.","Output was 1080x1920.","But roughly 70% was black bars.","I saw no captions. Audio was quiet.","Good at finding the moment.","Not ready to post as it came out.","What do you check before posting?"])
add("V04","Instagram","Short video",P3,"Your first line is the whole post",
 "Most people decide in the first two seconds. Put the answer first and cut the warm-up.",
 "What is your hook for tomorrow's post?",IG,beats=["Your first line is the whole post.","Say the answer first.","Cut the warm-up.","Weak: Hi everyone, today I want to talk about...","Better: Black bars waste your clip.","What is your hook for tomorrow?"])
add("V05","YouTube Shorts","Short video",P3,"Add captions. It costs nothing.",
 "Some people watch muted. Burned-in captions keep the idea readable without sound, and they are easy to check before you post.",
 "Do you caption every video?",YT,beats=["Add captions. It costs nothing.","Some people watch muted.","Burn them into the frame.","Keep each line short.","Check them before you post.","Do you caption every video?"])
add("V06","Instagram","Short video",P4,"My idea-to-post routine, in five steps",
 "A simple routine keeps posting steady: one idea, a draft, an edit, a native format per platform, then a scheduled slot.",
 "Which step slows you down most?",IG,beats=["Step one: write the idea in one sentence.","Step two: get a first draft.","Step three: edit it. Cut claims with no source.","Step four: shape it for each platform.","Step five: schedule it.","Which step slows you down most?"])
add("V07","YouTube Shorts","Short video",P1,"Resizing is not repurposing",
 "A letterboxed video is resized, not reframed. Reframing keeps the speaker in the frame and fills the screen.",
 "Do you reframe or just resize?",YT,beats=["Resizing is not repurposing.","A letterboxed video is just resized.","Black bars waste the screen.","Reframing keeps the speaker in view.","Then add captions.","Do you reframe or just resize?"])
add("V08","Instagram","Short video",P2,"I edited a draft by talking to it",
 "In IncuBrix I typed one idea into the box and picked a single LinkedIn post. It wrote a full draft, and I changed it with a chat message.",
 "How do you edit drafts today?",IG,["F1","F2","F3"],beats=["I typed one idea into IncuBrix.","It asked what kind of post I wanted.","I chose a single LinkedIn post.","It wrote a full draft.","I asked for a rewrite by chat.","The credit balance stays visible at the top.","How do you edit drafts today?"])
add("V09","YouTube Shorts","Short video",P5,"What 17 credits bought me",
 "A draft plus one rewrite cost 17 credits, from 300 to 283. One clip cost 13. Knowing the price per step helps you plan a month.",
 "Do you track what each step costs?",YT,["F3","F4"],beats=["What 17 credits bought me.","One draft plus one rewrite.","300 down to 283.","One clip cost 13 credits.","Know the price of each step.","Then plan the month.","Do you track what each step costs?"])
add("V10","Instagram","Short video",P4,"One idea. Three shapes.",
 "Turn one idea into a post, a carousel and a short video. Write a different first line for each so none of them feels copied.",
 "What idea could you reshape this week?",IG,beats=["One idea. Three shapes.","A LinkedIn post.","A carousel.","A short vertical video.","A different first line for each.","What idea could you reshape this week?"])

# ---------- 5 carousels ----------
add("C01","LinkedIn","Carousel",P1,"Stop pasting one graphic on every platform",
 "The same graphic on three platforms reads as copied on all three. Here is a simple way to adapt one idea without starting from zero.",
 "Which platform gets your idea first?",LI,slides=["Stop pasting one graphic on every platform","Each feed has its own shape and its own habits.","LinkedIn: context and a clear point of view.","Reels and Shorts: vertical, fast first line, captions.","Keep the idea. Change the first line and the frame.","Check it before it goes out: format, hook, caption, link.","Which platform gets your idea first?"])
add("C02","LinkedIn","Carousel",P3,"Five hook patterns that work for creators",
 "Hooks are easier when you pick a pattern. These five are plain and need no tricks.",
 "Which pattern will you try first?",LI,slides=["Five hook patterns for creators","The answer first: Black bars waste your clip.","The test: I tried X so you do not have to.","The mistake: Here is what I got wrong.","The question: What do you check before you post?","The before and after: 175 words, then under 150.","Which pattern will you try first?"])
add("C03","LinkedIn","Carousel",P4,"My idea-to-published workflow",
 "A repeatable routine matters more than a perfect post. This is the one I use for each idea.",
 "What would you change in this routine?",LI,slides=["My idea-to-published workflow","Step one: write the idea in one sentence.","Step two: get a first draft.","Step three: edit by instruction: length, claims, ending.","Step four: shape it for each platform.","Step five: add a tracking link and schedule it.","What would you change in this routine?"])
add("C04","LinkedIn","Carousel",P5,"Honest notes from my first session in IncuBrix",
 "I tested the LinkedIn Content template and Clips. Here is what worked, what did not, and what it cost.",
 "What would you want to know before trying it?",LI,["F1","F2","F3","F4","F5","F6","F7"],slides=["Honest notes from my first session","Worked: a draft from one typed idea.","Worked: a rewrite by chat followed all three instructions.","Cost: draft plus rewrite was 17 credits, 300 to 283.","Worked: Clips found one 32-second vertical clip. 13 credits.","Not ready: roughly 70% black bars, no captions seen, quiet audio.","Limit: Clips needs a source of at least 2 minutes. My 1:33 upload was rejected.","What would you want to know before trying it?"])
add("C05","Instagram","Carousel",P3,"A caption checklist before you post",
 "Run this list before every post. It takes a minute and catches most of the problems I see.",
 "What would you add to this checklist?",IG,slides=["A caption checklist before you post","First line: does it give the answer?","Claims: does every number have a source?","Call to action: one clear ask.","Hashtags: a few relevant ones.","Link: tracked, and placed where the platform allows it.","What would you add to this checklist?"])

# ---------- 5 graphics ----------
add("G01","Instagram","Graphic",P1,"Resized is not reformatted",
 "A letterboxed clip is the same video in a smaller box. Reframing it for vertical is a separate step.",
 "Do you reframe or resize?",IG,slides=["Resized is not reformatted."])
add("G02","Instagram","Graphic",P3,"Answer first. Warm-up never.",
 "The first line is the post. Lead with the answer and keep the warm-up out of it.",
 "What is your first line this week?",IG,slides=["Answer first. Warm-up never."])
add("G03","Instagram","Graphic",P5,"Check before you post: bars, captions, audio",
 "I check three things on every vertical clip: black bars, captions and audio level. One failed check means it is not ready.",
 "What is on your pre-post checklist?",IG,["F5"],slides=["Before you post a clip: check bars, captions, audio."])
add("G04","Instagram","Graphic",P4,"Idea, draft, edit, format, schedule",
 "Five steps, always in the same order. A routine you can repeat beats a clever one you cannot.",
 "Which step do you skip most?",IG,slides=["Idea. Draft. Edit. Format. Schedule."])
add("G05","Instagram","Graphic",P2,"Edit by instruction, not by hand",
 "In my test, one chat message asked for under 150 words, no unsourced claims, and a question at the end. The rewrite followed all three.",
 "What would you ask a rewrite to fix?",IG,["F2"],slides=["Under 150 words. No unsourced claims. End with a question."])

# ---------- 10 LinkedIn text posts ----------
def T(id,pillar,hook,body,cta,facts=()):
    add(id,"LinkedIn","Text post",pillar,hook,hook+"\n\n"+body,cta,LI,facts)
T("T01",P1,"Posting one video everywhere is not the same as posting well.",
 "Each platform has its own shape. LinkedIn rewards context. Reels and Shorts reward a fast first line and a vertical frame.\n\nI keep the idea and change three things: the first line, the frame and the ending.\n\nIt is slower than copy and paste. It also does not look copied.","Which of the three do you change first?")
T("T02",P5,"My first draft from an AI template ran long and cited numbers I could not source.",
 "I asked the LinkedIn Content template for a post under 150 words. The draft ran about 175, with figures that had no source, no hashtags and no call to action.\n\nOne rewrite by chat fixed the length, removed the claims and added a question.","Do you check every number in a draft before you post?",["F1","F2","F7"])
T("T03",P3,"The first line decides whether anyone reads the second.",
 "I write the answer first and cut anything that sounds like a warm-up.\n\nWeak: Today I want to share some thoughts on formatting.\nBetter: Black bars waste a vertical clip.\n\nThe second version tells you what you will learn before you decide to keep reading.","What is the first line of your next post?")
T("T04",P4,"I keep one routine for every idea: draft, edit, format, schedule.",
 "Posting stays steady when the routine is boring.\n\nFirst I write the idea in one sentence. Then I get a draft, edit it by instruction, shape it for each platform and add a tracked link.\n\nThe edit step is where most of the quality comes from.","Which step in your routine takes the longest?")
T("T05",P5,"A clip finder found my moment but I would not post the file.",
 "I ran a 2:25 landscape video through Clips. It found one 32-second clip at 1080x1920.\n\nRoughly 70% of the frame was black bars, I saw no captions in the frames I sampled, and the audio was quiet.\n\nThe finding step is useful. The finishing step is still on me.","What do you fix after a clip tool does its part?",["F4","F5"])
T("T06",P3,"Captions are the cheapest fix for a vertical video.",
 "Some people watch muted, so a video without captions loses them in the first seconds.\n\nBurn the captions into the frame, keep each line short, and read the whole video once with the sound off before you post.","Do you read your videos on mute before posting?")
T("T07",P2,"Editing a draft by chat is the part of IncuBrix I would use again.",
 "I typed one idea, chose a single LinkedIn post, and got a full draft. Then I asked for three changes in one message: under 150 words, remove two unsourced claims, end with a question.\n\nIt followed all three.","What would you ask a rewrite to change?",["F1","F2"])
T("T08",P1,"Resizing a video is not the same as reframing it.",
 "A landscape video squeezed into a vertical frame leaves bars above and below. The viewer sees a small picture inside a big screen.\n\nReframing follows the speaker and fills the frame. It is one more step, and it is the step that makes a clip look made for the platform.","Do you reframe, or resize and hope?")
T("T09",P5,"Know what each step costs before you plan a month of posts.",
 "In my test, one draft plus one rewrite cost 17 credits, from 300 to 283. One clip cost 13 credits.\n\nThe balance stayed visible at the top, which made it easy to see.\n\nMultiply that by your weekly plan before you commit.","Do you track the cost of each content step?",["F3","F4"])
T("T10",P4,"Turn one idea into three formats instead of three ideas.",
 "I take one idea and write a LinkedIn post, a short carousel and a vertical video from it.\n\nThe first line changes each time. The point stays the same. That way each feed gets something made for it, and I only have to think once.","What is one idea you could reuse this week?")
json.dump({"assets": A}, open("content/library_30.json", "w"), indent=1, ensure_ascii=False)
print(len(A), "assets")
