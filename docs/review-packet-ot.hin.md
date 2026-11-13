# Hindi OT guidelines — native-speaker review packet

Edition: Indian Revised Version (IRVHin). Source: Hebrew OT (WLCM). Draft guidelines: `docs/alignment-principles-ot.hin.md`.

**What we're asking.** Our alignment tool links Hindi words back to the Hebrew words they translate. These guidelines record how Hindi renders particular Hebrew constructions. Everything below was derived from reading the text and counting in the corpus; **none of it has been checked by a native Hindi speaker.** Please tell us where the description is wrong, unnatural, or too strong.

**You do not need to know the alignment tool.** The reviewer is assumed to read Hebrew and to know Bible translation. For each item: the claim, real verses (Hebrew + IRVHin), and a specific question. 'Defensible' is the bar — a reasonable rendering, not necessarily the only one.

**Method note.** Counts come from joining the Hebrew text to IRVHin by verse. They are pattern-level, not word-level alignment, so percentages are indicative.


## 1. न vs नहीं — distribution and register

**Claim.** in the OT, न is more than twice as frequent as नहीं (5,128 vs 2,334; मत 189) and the two are interchangeable for ordinary negation of לֹא.

**Verses**

- **Gen 2:5** (לֹא → नहीं)
  - Hebrew: וְ כֹל שִׂיחַ הַ שָּׂדֶה טֶרֶם יִהְיֶה בָ אָרֶץ וְ כָל עֵשֶׂב הַ שָּׂדֶה טֶרֶם יִצְמָח כִּי לֹא הִמְטִיר יְהוָה אֱלֹהִים עַל הָ אָרֶץ וְ אָדָם אַיִן לַ עֲבֹד אֶת הָ אֲדָמָה
  - IRVHin: तब मैदान का कोई पौधा भूमि पर न था, और न मैदान का कोई छोटा पेड़ उगा था, क्योंकि यहोवा परमेश्वर ने पृथ्वी पर जल नहीं बरसाया था, और भूमि पर खेती करने के लिये मनुष्य भी नहीं था।

- **Ps 23:1** (לֹא → न)
  - Hebrew: מִזְמוֹר לְ דָוִד יְהוָה רֹעִ י לֹא אֶחְסָר
  - IRVHin: यहोवा मेरा चरवाहा है, मुझे कुछ घटी न होगी। ( यशा. 40:11 )

**Question.** Is it accurate that न and नहीं are free variants here? Are there contexts (poetry vs narrative, tense, clause type) where one is clearly required or clearly marked?


## 2. 'Until' clauses carry an idiomatic न with no Hebrew source

**Claim.** in जब तक X न हो ('until X happens') the न has no correspondent in Hebrew עַד (no Hebrew negation). Found in 92% of IRVHin and 77%+ of OHCV जब तक clauses. The prompt treats this न/नहीं as NEQ target — a positive claim that it translates nothing.

**Verses**

- **Gen 27:44** (עַד אֲשֶׁר תָּשׁוּב חֲמַת אָחִיךָ)
  - Hebrew: וְ יָשַׁבְתָּ עִמּ וֹ יָמִים אֲחָדִים עַד אֲשֶׁר תָּשׁוּב חֲמַת אָחִי ךָ
  - IRVHin: और थोड़े दिन तक, अर्थात् जब तक तेरे भाई का क्रोध न उतरे तब तक उसी के पास रहना।

- **Exod 24:14** (עַד אֲשֶׁר נָשׁוּב אֲלֵיכֶם)
  - Hebrew: וְ אֶל הַ זְּקֵנִים אָמַר שְׁבוּ לָ נוּ בָ זֶה עַד אֲשֶׁר נָשׁוּב אֲלֵי כֶם וְ הִנֵּה אַהֲרֹן וְ חוּר עִמָּ כֶם מִי בַעַל דְּבָרִים יִגַּשׁ אֲלֵ הֶם
  - IRVHin: और पुरनियों से वह यह कह गया, “ जब तक हम तुम्हारे पास फिर न आएँ तब तक तुम यहीं हमारी बाट जोहते रहो; और सुनो, हारून और हूर तुम्हारे संग हैं; तो यदि किसी का मुकद्दमा हो तो उन्हीं के पास जाए।”

- **Josh 10:13** 
  - Hebrew: וַ יִּדֹּם הַ שֶּׁמֶשׁ וְ יָרֵחַ עָמָד עַד יִקֹּם גּוֹי אֹיְבָי ו הֲ לֹא הִיא כְתוּבָה עַל סֵפֶר הַ יָּשָׁר וַ יַּעֲמֹד הַ שֶּׁמֶשׁ בַּ חֲצִי הַ שָּׁמַיִם וְ לֹא אָץ לָ בוֹא כְּ יוֹם תָּמִים
  - IRVHin: और सूर्य उस समय तक थमा रहा; और चन्द्रमा उस समय तक ठहरा रहा, जब तक उस जाति के लोगों ने अपने शत्रुओं से बदला न लिया। क्या यह बात याशार नामक पुस्तक में नहीं लिखी है कि सूर्य आकाशमण्डल के बीचोबीच ठहरा रहा, और लगभग चार पहर तक न डूबा?

**Question.** Is the न in these clauses a required part of the Hindi 'until' construction (vs optional / stylistic)? Is NEQ the right call, or would you say it is a grammatical marker of the clause that belongs with जब तक?


## 3. 'Before' (עַד אֲשֶׁר לֹא) with no Hindi negator

**Claim.** Hebrew עַד אֲשֶׁר לֹא in Ecclesiastes 12 ('before ...') is rendered इससे पहले कि ... with no negator; the Hebrew לֹא has no Hindi counterpart. Prompt recommends grouping עַד אֲשֶׁר לֹא as one lexicalized 'before' unit.

**Verses**

- **Eccl 12:1** 
  - Hebrew: וּ זְכֹר אֶת בּוֹרְאֶי ךָ בִּ ימֵי בְּחוּרֹתֶי ךָ עַד אֲשֶׁר לֹא יָבֹאוּ יְמֵי הָ רָעָה וְ הִגִּיעוּ שָׁנִים אֲשֶׁר תֹּאמַר אֵין לִ י בָ הֶם חֵפֶץ
  - IRVHin: अपनी जवानी के दिनों में अपने सृजनहार को स्मरण रख, इससे पहले कि विपत्ति के दिन और वे वर्ष आएँ, जिनमें तू कहे कि मेरा मन इनमें नहीं लगता।

- **Eccl 12:2** 
  - Hebrew: עַד אֲשֶׁר לֹא תֶחְשַׁךְ הַ שֶּׁמֶשׁ וְ הָ אוֹר וְ הַ יָּרֵחַ וְ הַ כּוֹכָבִים וְ שָׁבוּ הֶ עָבִים אַחַר הַ גָּשֶׁם
  - IRVHin: इससे पहले कि सूर्य और प्रकाश और चन्द्रमा और तारागण अंधेरे हो जाएँ, और वर्षा होने के बाद बादल फिर घिर आएँ;

**Question.** Is 'पहले कि' the natural rendering? Does it ever take a न in similar clauses? Is it reasonable to treat עַד אֲשֶׁר לֹא as one unit mapped to पहले कि?


## 4. आप (ही) — intensive/agentive reflexive

**Claim.** आप / आप ही is productive (~175 IRVHin occurrences). Three treatments: (a) with an explicit Hebrew pronoun, both Hindi pronoun and आप are primary to it; (b) with no Hebrew trigger it is a supplied emphasis → secondary to the noun/verb; (c) fixed 'आप से आप' = 'of itself' maps to the Hebrew lexeme (e.g. סָפִיחַ).

**Verses**

- **Gen 3:5** (b)
  - Hebrew: כִּי יֹדֵעַ אֱלֹהִים כִּי בְּ יוֹם אֲכָלְ כֶם מִמֶּ נּוּ וְ נִפְקְחוּ עֵינֵי כֶם וִ הְיִיתֶם כֵּ אלֹהִים יֹדְעֵי טוֹב וָ רָע
  - IRVHin: वरन् परमेश्वर आप जानता है कि जिस दिन तुम उसका फल खाओगे उसी दिन तुम्हारी आँखें खुल जाएँगी, और तुम भले बुरे का ज्ञान पाकर परमेश्वर के तुल्य हो जाओगे।”

- **Num 16:5** (b)
  - Hebrew: וַ יְדַבֵּר אֶל קֹרַח וְ אֶל כָּל עֲדָת וֹ לֵ אמֹר בֹּקֶר וְ יֹדַע יְהוָה אֶת אֲשֶׁר ל וֹ וְ אֶת הַ קָּדוֹשׁ וְ הִקְרִיב אֵלָי ו וְ אֵת אֲשֶׁר יִבְחַר בּ וֹ יַקְרִיב אֵלָי ו
  - IRVHin: फिर उसने कोरह और उसकी सारी मण्डली से कहा, “ सवेरे को यहोवा दिखा देगा कि उसका कौन है, और पवित्र कौन है, और उसको अपने समीप बुला लेगा; जिसको वह आप चुन लेगा उसी को अपने समीप बुला भी लेगा।

- **Gen 22:8** (Hebrew לוֹ 'for himself')
  - Hebrew: וַ יֹּאמֶר אַבְרָהָם אֱלֹהִים יִרְאֶה לּ וֹ הַ שֶּׂה לְ עֹלָה בְּנִ י וַ יֵּלְכוּ שְׁנֵי הֶם יַחְדָּו
  - IRVHin: अब्राहम ने कहा, “ हे मेरे पुत्र, परमेश्वर होमबलि की भेड़ का उपाय आप ही करेगा।” और वे दोनों संग-संग आगे चलते गए।

- **Lev 25:5** (c)
  - Hebrew: אֵת סְפִיחַ קְצִירְ ךָ לֹא תִקְצוֹר וְ אֶת עִנְּבֵי נְזִירֶ ךָ לֹא תִבְצֹר שְׁנַת שַׁבָּתוֹן יִהְיֶה לָ אָרֶץ
  - IRVHin: जो कुछ काटे हुए खेत में अपने आप से उगें उसे न काटना, और अपनी बिन छाँटी हुई दाखलता की दाखों को न तोड़ना; क्योंकि वह भूमि के लिये परमविश्राम का वर्ष होगा।

**Question.** Is आप here best described as an emphatic/intensive reflexive, an honorific, or something else? Does 'supplied emphasis' correctly describe cases like Gen 3:5 where Hebrew has no pronoun?


## 5. 'No longer' (לֹא ... עוֹד) is usually discontinuous

**Claim.** ~82% of 'no longer' renderings separate फिर from न (e.g. फिर कभी ... न). आगे को is a real alternative to फिर.

**Verses**

- **Gen 8:12** 
  - Hebrew: וַ יִּיָּחֶל עוֹד שִׁבְעַת יָמִים אֲחֵרִים וַ יְשַׁלַּח אֶת הַ יּוֹנָה וְ לֹא יָסְפָה שׁוּב אֵלָי ו עוֹד
  - IRVHin: फिर उसने सात दिन और ठहरकर उसी कबूतरी को उड़ा दिया; और वह उसके पास फिर कभी लौटकर न आई।

- **Gen 9:11** 
  - Hebrew: וַ הֲקִמֹתִי אֶת בְּרִיתִ י אִתְּ כֶם וְ לֹא יִכָּרֵת כָּל בָּשָׂר עוֹד מִ מֵּי הַ מַּבּוּל וְ לֹא יִהְיֶה עוֹד מַבּוּל לְ שַׁחֵת הָ אָרֶץ
  - IRVHin: और मैं तुम्हारे साथ अपनी यह वाचा बाँधता हूँ कि सब प्राणी फिर जल-प्रलय से नाश न होंगे और पृथ्वी का नाश करने के लिये फिर जल-प्रलय न होगा।”

**Question.** Does separated फिर ... न sound natural, and is the contiguous फिर कभी न equally natural (a stylistic option) or marked?


## 6. Passive strategies for Niphal/Pual/Hophal

**Claim.** eight coexisting strategies (जाना-periphrastic, stative/resultative, adjective + होना, dedicated intransitive, light-verb, naming/equational, ...) with no single default.

**Verses**

- **Isa 53:5** (Pual: घायल किया गया, कुचला गया; Niphal: चंगे हो जाएँ)
  - Hebrew: וְ הוּא מְחֹלָל מִ פְּשָׁעֵ נוּ מְדֻכָּא מֵ עֲוֺנֹתֵי נוּ מוּסַר שְׁלוֹמֵ נוּ עָלָי ו וּ בַ חֲבֻרָת וֹ נִרְפָּא לָ נוּ
  - IRVHin: परन्तु वह हमारे ही अपराधों के कारण घायल किया गया, वह हमारे अधर्म के कामों के कारण कुचला गया; हमारी ही शान्ति के लिये उस पर ताड़ना पड़ी कि उसके कोड़े खाने से हम लोग चंगे हो जाएँ। ( रोम. 4:25, 1 पत. 2:24 )

- **Gen 21:5** (Niphal: उत्पन्न हुआ)
  - Hebrew: וְ אַבְרָהָם בֶּן מְאַת שָׁנָה בְּ הִוָּלֶד ל וֹ אֵת יִצְחָק בְּנ וֹ
  - IRVHin: जब अब्राहम का पुत्र इसहाक उत्पन्न हुआ तब वह एक सौ वर्ष का था।

- **Gen 2:23** (Niphal: 'she shall be called' → इसका नाम नारी होगा)
  - Hebrew: וַ יֹּאמֶר הָ אָדָם זֹאת הַ פַּעַם עֶצֶם מֵ עֲצָמַ י וּ בָשָׂר מִ בְּשָׂרִ י לְ זֹאת יִקָּרֵא אִשָּׁה כִּי מֵ אִישׁ לֻקֳחָה זֹּאת
  - IRVHin: तब आदम ने कहा, “ अब यह मेरी हड्डियों में की हड्डी और मेरे माँस में का माँस है; इसलिए इसका नाम नारी होगा, क्योंकि यह नर में से निकाली गई है।”

**Question.** Are these genuinely passive in Hindi or just intransitive/active? Is anything we list as a passive strategy actually not a passive?


## 7. Genitive का/की/के and construct chains

**Claim.** Relational/human construct chains are rendered with का/की/के agreeing with the possessed noun (≈90–96% for בֵּן, מֶלֶךְ, בַּיִת). BUT a geographic head + place name is usually bare apposition with no postposition: אֶרֶץ+name → "मिस्र देश" (77%; never "मिस्र का देश"), הַר+name → "सीनै पर्वत" (~76%), נָהָר+name → "यरदन नदी".

**Verses**

- **Josh 1:1** 
  - Hebrew: וַ יְהִי אַחֲרֵי מוֹת מֹשֶׁה עֶבֶד יְהוָה וַ יֹּאמֶר יְהוָה אֶל יְהוֹשֻׁעַ בִּן נוּן מְשָׁרֵת מֹשֶׁה לֵ אמֹר
  - IRVHin: यहोवा के दास मूसा की मृत्यु के बाद यहोवा ने उसके सेवक यहोशू से जो नून का पुत्र था कहा,

- **Gen 13:10** (אֶרֶץ מִצְרַיִם → "मिस्र देश")
  - Hebrew: וַ יִּשָּׂא לוֹט אֶת עֵינָי ו וַ יַּרְא אֶת כָּל כִּכַּר הַ יַּרְדֵּן כִּי כֻלָּ הּ מַשְׁקֶה לִ פְנֵי שַׁחֵת יְהוָה אֶת סְדֹם וְ אֶת עֲמֹרָה כְּ גַן יְהוָה כְּ אֶרֶץ מִצְרַיִם בֹּאֲ כָה צֹעַר
  - IRVHin: तब लूत ने आँख उठाकर, यरदन नदी के पास वाली सारी तराई को देखा कि वह सब सिंची हुई है। जब तक यहोवा ने सदोम और गमोरा को नाश न किया था, तब तक सोअर के मार्ग तक वह तराई यहोवा की वाटिका, और मिस्र देश के समान उपजाऊ थी।
- **Gen 13:12** (אֶרֶץ כְּנַעַן → "कनान देश")
  - Hebrew: אַבְרָם יָשַׁב בְּ אֶרֶץ כְּנָעַן וְ לוֹט יָשַׁב בְּ עָרֵי הַ כִּכָּר וַ יֶּאֱהַל עַד סְדֹם
  - IRVHin: अब्राम तो कनान देश में रहा, पर लूत उस तराई के नगरों में रहने लगा; और अपना तम्बू सदोम के निकट खड़ा किया।
- **Exod 19:11** (הַר סִינַי → "सीनै पर्वत")
  - Hebrew: וְ הָיוּ נְכֹנִים לַ יּוֹם הַ שְּׁלִישִׁי כִּי בַּ יּוֹם הַ שְּׁלִישִׁי יֵרֵד יְהוָה לְ עֵינֵי כָל הָ עָם עַל הַר סִינָי
  - IRVHin: और वे तीसरे दिन तक तैयार हो जाएँ; क्योंकि तीसरे दिन यहोवा सब लोगों के देखते सीनै पर्वत पर उतर आएगा।
- **2 Kgs 19:31** (הַר צִיּוֹן → "सिय्योन पर्वत")
  - Hebrew: כִּי מִ ירוּשָׁלִַם תֵּצֵא שְׁאֵרִית וּ פְלֵיטָה מֵ הַר צִיּוֹן קִנְאַת יְהוָה צְבָאוֹת תַּעֲשֶׂה זֹּאת
  - IRVHin: क्योंकि यरूशलेम में से बचे हुए और सिय्योन पर्वत के भागे हुए लोग निकलेंगे। यहोवा यह काम अपनी जलन के कारण करेगा।

**Question.** Is "मिस्र देश" / "सीनै पर्वत" (no का) the normal, natural form, and "मिस्र का देश" unnatural or merely rarer? Where else does Hindi use apposition instead of का/की/के (titles, compounds, person names)?


## 8. Purpose infinitive: को vs के लिये

**Claim.** for לְ + infinitive construct, को (40%) is at least as common as के लिये (24%) in a 25-verse sample (excluding לֵאמֹר, which → कि).

**Verses**

- **Gen 2:5** (לַעֲבֹד → करने के लिये)
  - Hebrew: וְ כֹל שִׂיחַ הַ שָּׂדֶה טֶרֶם יִהְיֶה בָ אָרֶץ וְ כָל עֵשֶׂב הַ שָּׂדֶה טֶרֶם יִצְמָח כִּי לֹא הִמְטִיר יְהוָה אֱלֹהִים עַל הָ אָרֶץ וְ אָדָם אַיִן לַ עֲבֹד אֶת הָ אֲדָמָה
  - IRVHin: तब मैदान का कोई पौधा भूमि पर न था, और न मैदान का कोई छोटा पेड़ उगा था, क्योंकि यहोवा परमेश्वर ने पृथ्वी पर जल नहीं बरसाया था, और भूमि पर खेती करने के लिये मनुष्य भी नहीं था।

**Question.** Is there a semantic difference between को and के लिये as purpose markers in these sentences?
