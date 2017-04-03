Someone once told me that no such converter existed and, even if there was, it
would be a waste of time because each vendor's OS is too diverse to make it
feasible. It surprised me though that most of the bigger brands didn't have
CLI guides to help network engineers/sysadmins make the transition from one
vendor to another. It surprised me more that nobody tried to automate this and
offer up the script to the public.

In one of my previous jobs, we went through two years of major network
upgrades. FastEthernet switches were being removed in buildings with
cross-connect and equipment being upgraded to gig. I prepared over 1,500
wireless APs and 75 Cisco switches. While configuration would remain mostly the
same, going from one model to another (e.g. Cisco 3750 stack to 3850 or 4506)
required changing interface names, trimming out incompatible configuration,
and moving connections from one interface to another — some blades were
consolidated or for other reasons. We created a script that would change all of
this for us (a scrubbed version will be in the examples folder) and it worked
rather well.

I wanted to share that script (and was given permission by my employer) for
others to use, but I wanted to make it more modular, more flexible, and while
I'm at it, make it cross-vendor compatible. I don't care if it's not feasible,
if you think it's stupid, or if you think it's too niche. The fact is that at
least two different engineers come across the same issue and could really use
it.

So let's do it.