# WordNet To Anything
This is mainly a python3 script to help you port Wordnet data structures to another language, database, or anything you might be intersted. It reads each line of the wordnet text files and returns a python dictionary containing the tokens; then you can do whatever you want with this dictionary. The `dict_to_mongo.py` script, for example, takes each dictionary and inserts as a document in a MongoDB database (of course it separates each text file in its own collection).


You can insert everything into MongoDB, but since RAM today is big, you can fit the entire WordNet into it, which will lead to 
faster searching (you'll, though, have to implement your own searching algorithm in some languages). Remember that you don't have to rewrite
this parser to other languages in order to have the WordNet accessible through RAM into your prefered one, you just have to save the WordNet
in json files and parse them with your language's json parser (maybe I'll create a .json version of WordNet and link it here).

# How to use it

Just make sure that you have pymongo (optional but you might wanna use it): `pip3 install pymongo`

```
git clone https://github.com/lattice0/wordnetToAnything

cd wordnetToAnything

python3 dict_to_json.py
```

to see what it can do.

# How WordNet works (internals, file formats, synset relations)
You might be intersted in a better explanation of the WordNet data files than the one shown in the documentation. It was a little hard for me to 
understand how the WordNet works just by looking into the official documentation, so I hope this article serves you well.

[This][4] is where you can download the WordNet. However, it comes with programs to read the data. We just want the data, as we're gonna building programs on top of it, or just intersted in converting it to another language. So you should download from the part that says "WordNet 3.1 DATABASE FILES ONLY". You'll get the following files:

`adj.exc, adv.exc, cntlist, cntlist.rev, cousin.exc, data.adj, data.adv, data.noun, data.verb, dbfiles, index.adj, index.adv, index.noun, index.sense, index.verb, log.grind.3.1, noun.exc, sentidx.vrb, sents.vrb, verb.exc, verb.Framestext`

The ones that really matter are `index.something` and `data.something`, where this `something` can be `adv`, `noun`, `verbe`, `adj`


The article below is a better written version from [this discussion][3] I had on stackoverflow:

So, if we want to know something about the word `dog` as a `noun`, we must look into the `index.noun` file and search for the word `dog`, which gives us the line:

    dog n 7 5 @ ~ #m #p %p 7 1 02086723 10133978 10042764 09905672 07692347 03907626 02712903  

According to the WNDB documment, this line represents these data:

    lemma  pos  synset_cnt  p_cnt  [ptr_symbol...]  sense_cnt  tagsense_cnt   synset_offset  [synset_offset...] 

Where `lemma` is the word, `pos` is the identifier that tells it's a noun, `synset_cnt` tells us in how many synsets this word is included, `p_cnt` tells us how many pointers to these synsets we have, `[ptr_symbol]` is an array of pointers, `sense_cnt` and `tagsense_cnt` are some data I havent figured out the purpose yet, and `synset_offset` is one or more synsets to be looked into the `data.noun` file

Ok, so those pointers must point to something, and here are their descriptions (cutted only the ones that appear in dog), as written in WNINPUT:

    @    Hypernym 
     ~    Hyponym 
    #m    Member holonym 
    #p    Part holonym 
    %p    Part meronym 

The other important fields to be looked are `synset_offset`s, which in the dog case are:

    02086723 10133978 10042764 09905672 07692347 03907626 02712903  

Let's look at the first one, `02086723`, in `data.noun`:

    02086723 05 n 03 dog 0 domestic_dog 0 Canis_familiaris 0 023 @ 02085998 n 0000 @ 01320032 n 0000 #m 02086515 n 0000 #m 08011383 n 0000 ~ 01325095 n 0000 ~ 02087384 n 0000 ~ 02087513 n 0000 ~ 02087924 n 0000 ~ 02088026 n 0000 ~ 02089774 n 0000 ~ 02106058 n 0000 ~ 02112993 n 0000 ~ 02113458 n 0000 ~ 02113610 n 0000 ~ 02113781 n 0000 ~ 02113929 n 0000 ~ 02114152 n 0000 ~ 02114278 n 0000 ~ 02115149 n 0000 ~ 02115478 n 0000 ~ 02115987 n 0000 ~ 02116630 n 0000 %p 02161498 n 0000 | a member of the genus Canis (probably descended from the common wolf) that has been domesticated by man since prehistoric times; occurs in many breeds; "the dog barked all night" 

As you can see, we've found the line that begins with `02086723`. The contents of this line are described in WNDB as:

    synset_offset  lex_filenum  ss_type  w_cnt  word  lex_id  [word  lex_id...]  p_cnt  [ptr...]  [frames...]  |   gloss 

synset_offset we already know, 

`lex_filenum` says in which of the lexicographers file is our word (lexicographer files are not important for now), 

`ss_type` is `n` which tells us that it's a noun, 

`w_cnt`: two digit hexadecimal integer indicating the number of words in the synset, which in this case is `03`, which means we have 3 words in this synset: `dog 0 domestic_dog 0 Canis_familiaris 0`, each one followed by a number called:

`lex_id`: one digit hexadecimal integer that, when appended onto lemma , uniquely identifies a sense within a lexicographer file

  [1]: https://wordnet.princeton.edu/wordnet/man/wndb.5WN.html
  [2]: https://wordnet.princeton.edu/wordnet/man/wninput.5WN.html
  [3]: https://stackoverflow.com/questions/42216995/what-exactly-are-wordnet-lexicographer-files-understanding-how-wordnet-works
  [4]: https://wordnet.princeton.edu/wordnet/download/current-version/
    p_cnt: counts the number of pointers, which in our case is `023`, so we have 23 pointers, wow

After `p_cnt`, then comes the pointers, each one in the format:

    pointer_symbol  synset_offset  pos  source/target 

Where `pointer_symbol` is about the symbols like the ones I showed (@, ~, ...), 

`synset_offset`: is the byte offset of the target synset in the data file corresponding to `pos` 

`source/target`: field distinguishes lexical and semantic pointers. It is a four byte field, containing two two-digit hexadecimal integers. The first two digits indicates the word number in the current (source) synset, the last two digits indicate the word number in the target synset. A value of 0000 means that pointer_symbol represents a semantic relation between the current (source) synset and the target synset indicated by synset_offset .

Ok, so let's examine the first pointer:

    @ 02085998 n 0000

It's a pointer with symbol `@`, indicating it's a `Hypernym`, and points to the synset wiuth offset `02085998` of type `n` (noun), and `source/target` is `0000`

When I search for  in data.noun, I get 

    02085998 05 n 02 canine 0 canid 0 011 @ 02077948 n 0000 #m 02085690 n 0000 + 02688440 a 0101 ~ 02086324 n 0000 ~ 02086723 n 0000 ~ 02116752 n 0000 ~ 02117748 n 0000 ~ 02117987 n 0000 ~ 02119787 n 0000 ~ 02120985 n 0000 %p 02442560 n 0000 | any of various fissiped mammals with nonretractile claws and typically long muzzles  

which is an `Hypernym` of `dog`. So that's how you find relations betweet synsets. 
