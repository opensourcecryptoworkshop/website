+++
title = "OSCW 2026: Taipei, Taiwan"
description = "OSCW 2026 will take place 8 March 2026, the day before Real World Crypto"
weight = 47
+++

OSCW 2026 will take place before [Real World Crypto](https://rwc.iacr.org/2026/) as an [affiliated event](https://realworldcrypto.iacr.org/2026/affiliated.php) on 8 March 2026 at the [Biomedical Translation Research Center](https://maps.app.goo.gl/hRgVz3kRcHLRBacP6) at [Academia Sinica](https://www.sinica.edu.tw/en) in Taipei, Taiwan.

## Registration

Since OSCW is an affiliated event of RWC, attendees register for this workshop via [the IACR portal](https://rwc.iacr.org/2026/registration.php). It is possible to register _only_ for OSCW without registering for RWC.

**Note: As the sponsor of OSCW 2026, Google will cover the [cost of attending OSCW](https://rwc.iacr.org/2026/registration.php) (150 USD) if your organization is not covering your registration fee. Please apply by filling out [this form](https://forms.gle/mj1YP7WrfSKEm9EC6).**

The waiver token must be used when you register, as it cannot be retroactively applied. The organizers will be in touch with waiver tokens within 1 week of your submission.

## Tentative Schedule

### **8:00 - 9:00** Breakfast / Registration

### **9:00 - 9:30** Integrating Post-Quantum algorithms into a crypto library: case study in GnuTLS
{{% expand title="Daiki Ueno" %}} As a core maintainer of GnuTLS since 2020, Daiki has been architecting the secure communications library to meet modern security standards. He works at Red Hat, where his primary focus is post-quantum migration of RHEL. He is also an active contributor to essential cryptographic libraries throughout the ecosystem, including Nettle, p11-kit, and NSS. {{% /expand %}}

{{% expand title="Abstract" %}}
GnuTLS is a free software implementation of the TLS and DTLS protocols, particularly popular in the areas of desktop and virtualization. Like other major libraries, GnuTLS is actively integrating Post-Quantum Cryptography (PQC) to ensure the future security of digital communication against the threat of quantum computing. Our journey began with prototyping using liboqs at the IETF hackathon, followed by transitioning to another implementation, leancrypto, for certification and performance reasons. Looking ahead, our current focus is to introduce a native PQC implementation via the Nettle cryptographic library, the default GnuTLS backend, motivated by a desire for consistent licensing across the ecosystem and the strategic advantage of increasing implementation diversity to mitigate single-source risks.

Implementing these complex lattice-based cryptographic primitives in C has presented several technical challenges that we feel are important to share with the community. We will detail common pitfalls, such as securing against potential side-channel vulnerabilities, where operations dependent on secret data require strict constant-time coding, and addressing the memory allocation and management complexities inherent in PQC's polynomial and matrix operations. Our presentation will outline the strategies we have adopted, including branchless coding where feasible, rigorously zeroing memory to prevent leakage, avoiding signed integer overflow, and implementing dedicated constant-time validation tests.
{{% /expand %}}

### **9:30 - 10:00** AWS-LC: Deploying Formally Verified Post-Quantum Cryptography at Scale
{{% expand title="Dusan Kostic" %}} Dusan Kostic is a cryptographer at AWS, where he focuses on post-quantum cryptography and formal verification. A core developer and maintainer of the AWS-LC cryptographic library, he also contributes regularly to mlkem-native and s2n-bignum. He holds a PhD from EPFL, where he was advised by Arjen Lenstra, and mentored by Shay Gueron. {{% /expand %}}

{{% expand title="Abstract" %}}
AWS-LC is Amazon's open-source cryptographic library, powering billions of daily cryptographic operations across security-critical AWS services. As the cryptographic foundation for AWS, the library undergoes yearly FIPS validation and demands the highest levels of assurance. With the threat of ""store now, decrypt later"" quantum attacks driving AWS's post-quantum migration plan, integrating high-assurance ML-KEM support into AWS-LC has been a critical priority.
This talk describes how we developed and integrated mlkem-native, an optimized and formally verified ML-KEM implementation developed under the Post-Quantum Cryptography Alliance (PQCA), into AWS-LC. Building on the ML-KEM reference implementation, mlkem-native adds optimized assembly backends achieving 2.08x-2.78x performance improvements on Graviton processors and 1.5x-2.0x on x86, while providing formal verification guarantees across both C and assembly layers. This implementation is now part of AWS-LC's 2025-2026 FIPS validation cycle.

AWS-LC's reach extends well beyond AWS services. Through aws-lc-rs, a Rust cryptographic library built on AWS-LC, it serves as the default cryptographic provider for rustls, a widely adopted TLS library. The underlying mlkem-native implementation has also been adopted as the default ML-KEM in libOQS, part of the Open Quantum Safe project.

We discuss our verification strategy: CBMC verifies the C code for memory-safety, type-safety, and in some cases functional correctness, using contracts and loop invariants, while HOL Light verifies the hand-crafted assembly for functional correctness using the s2n-bignum infrastructure. We explain how these verification domains connect at the C-assembly boundary, how we keep proofs synchronized with code through CI, and our ongoing work on constant-time verification. We reflect on lessons learned from deploying formally verified post-quantum cryptography into a production library at AWS scale.
{{% /expand %}}


### **10:00 - 10:30** Forward Secrecy for Signal Secure Backups
{{% expand title="Graeme Connell (he/him)" %}} Graeme Connell is a software developer on the Research team at Signal nonprofit, where he has worked since 2021. At Signal, he has focused on systems running in Trusted Execution Environments, including the ORAM-backed Contact Discovery Service and rollback-resistant Secure Value Recovery Service. He has also been a key contributor to Signal's post-quantum migration, including development of the Sparse Post-Quantum Ratchet and current work on session management systems and scalability improvements for Signal's private group system. Prior to Signal, Graeme spent 14 years with Google working on authorization, intrusion detection and response, websearch, geo, and payments security. Graeme currently resides in British Columbia, Canada. {{% /expand %}}

{{% expand title="Abstract" %}}
Forward Secrecy is one of the cryptographic goals we strive to achieve throughout Signal - if you sent a message last year, that message has since been deleted (due to disappearing messages, manual deletion, etc), then your device is compromised today, how do we disallow the attacker from accessing that old message?  While the message is being sent and received, we utilize our ratcheting protocols, but what about for backups?  A backup must use a predefined static key, or users wouldn't be able to restore their old backups in the case where their devices were lost or destroyed.  But reusing the same key for all backups negates forward secrecy - an attacker could have access to copies of old backups, and on learning the static key they could decrypt all past backups and get access to your old messages.

Signal already has a system in place for account recovery that uses a predefined key to access secret material, called Secure Value Recovery.  In this system, a collection of remote enclaves encrypts and stores a set of secrets and associated PINs.  A user can access the secret by providing their PIN, and with that secret they can then prove to Signal's other servers that they're associated with a particular account and regain access to it.  When we looked at the problem of Backup Forward Secrecy, we observed multiple similarities.  So, we used a new deployment of our existing system to store secret material that could be used to recreate a Forward Secrecy Token - a secret that can be mixed into a backup's encryption secret on a per-backup basis, then rewritten once a new backup is created.  By effectively storing forward secrecy tokens in a secure, rewritable database, we're able to forget old secrets by overwriting them with new ones, preserving Forward Secrecy.

In this talk, we'll discuss the problem of Forward Secrecy in Backups, the decision to reuse existing infrastructure in a new way rather than building something new from scratch, and the integration of the resulting Forward Secrecy Tokens (FSTs) into the encryption of backups that allows the property of Forward Secrecy to be attained.  We'll discuss the protocols for storing, retrieving, overwriting, and deleting FSTs, as well as the way that FSTs are integrated into the encryption of stored backups.  We'll also discuss the ways we've created a system where a newly generated backup can be stored remotely along with its associated FST, such that a failure during any step still allows for a recent backup to be restored.
{{% /expand %}}

### **10:30 - 11:00** *Morning coffee break*

### **11:00 - 12:00** *To Be Announced*

### **12:00 - 12:30** Footguns, Open Source, and WTF, Guys? Seriously?
{{% expand title="Opal Wright (she/her)" %}} &nbsp; {{% /expand %}}

{{% expand title="Abstract" %}}
Some of the most popular open source cryptography libraries are footgun-filled horror shows. According to GitHub, aes-js has over 700k direct and indirect dependents, and its CTR implementation “helpfully” supplies a fixed, default counter. Its sister library, pyaes, makes the same design decision and gives examples that rely on this behavior in the documentation. elliptic.js has serious bugs that went unaddressed for the better part of a decade. libgcrypt, which underpins GnuPG, provides single-DES, RC4, MD4, and other insecure primitives available to developers, despite not being supported in the OpenPGP standard.

These footguns lead to real-world failures: Trail of Bits has identified multiple applications, including cryptocurrency wallets, a password manager, and a VPN management suite, that have relied on the aes-js/pyaes default IV, severely compromising wallets, certificates, passwords, and passphrases. elliptic.js led to real-world signature failures.

Why the hell is this situation allowed to continue? Failing to speak openly and loudly about these popular libraries is cryptographic malpractice, and we have to do more to protect developers. Better APIs can only go so far: it’s time for us to start naming names and warning against bad actors.
{{% /expand %}}
### **12:30 - 14:00** *Lunch break*
### **14:00 - 15:00** *To Be Announced*
### **15:00 - 15:30** Lessons Learned from Working with Verified Code in libcrux
{{% expand title="Jonas Schneider-Bensch (he/him)" %}} &nbsp; {{% /expand %}}

{{% expand title="Abstract" %}}
The libcrux library of formally verified cryptographic algorithms exhibits a spectrum of different techniques for increasing the level of assurance that can be placed in the code. These range from leveraging the Rust type system to enforce length bounds and secret independent operations to translating from Rust code into an external proof system to establish functional correctness. In this presentation I’ll share how these different approaches interact with and shape the work of maintaining and developing the library, code of which is integrated e.g. in Signal, Firefox and OpenSSH. In particular, I’ll show which benefits are conveyed to cryptographic engineers, but also where limitations may hinder development.

The presentation should be of interest to anyone working with high assurance cryptographic code in production environments, from either the cryptographic engineering or tool maker perspective and I want to invite you to open discussion afterwards on high assurance development practices.
{{% /expand %}}

### **15:30 - 16:00** *Afternoon coffee break*
### **16:00 - 16:30** Mopro: Making Client-Side Zero-Knowledge Proving on Mobile Simple

{{% expand title="Moven Tsai and Vivian Jeng" %}}
Vivian Jeng: Developer at Ethereum Foundation (PSE)
Moven Tsai: Developer at Ethereum Foundation (PSE) {{% /expand %}}

{{% expand title="Abstract" %}}
Mopro is an open-source toolkit for client-side ZK proving on mobile. It lets developers port Rust-based ZK circuits to iOS, Android, React Native, Flutter, and web/WASM with minimal effort.

###### What Mopro provides
- Cross-platform bindings generation via CLI (Swift, Kotlin, WASM, etc.)
- Support for Circom, Halo2, and Noir circuits
- Also suitable for other computation-intensive protocols like FHE in Rust crates
- Up to 20x faster proving compared to browser-based snarkjs

###### Session content
1. Architecture overview: how FFIs enable cross-platform support
2. Live demo: scaffold a ZK mobile app using `mopro-cli` and generate a proof on a real device
3. Real-world usage: Anon Aadhaar, zkEmail, EZKL, Semaphore

###### Links
- Website: https://zkmopro.org
- GitHub: https://github.com/zkmopro/mopro (210+ stars, 51 contributors, Apache-2.0/MIT)
- Previous talks: https://zkmopro.org/docs/community
{{% /expand %}}

### **16:30 - 17:00** Implementations of Anonymous Tokens with & without Metadata

{{% expand title="Ghous Amjad (he/him)" %}} &nbsp; {{% /expand %}}

{{% expand title="Abstract" %}}
In this talk, I will discuss the open-source cryptography code that my team at Google has been maintaining for the last five years, which is used in many Google products. This includes two GitHub repositories: "Private Set Membership" (https://github.com/google/private-membership) and "Anonymous Tokens" (https://github.com/google/anonymous-tokens). The talk will focus primarily on the latter, touching on topics ranging from protocol design and deployment challenges to the requirements and needs that led to open-sourcing the code. I will also discuss why public metadata is useful for anonymous tokens, the trade-off between anonymity and tracking bits, and how we enabled this in our protocol. I will cover several main deployment challenges, such as the limited number of libraries our code could depend on for various reasons, supporting multiple languages, attempting to be constant-time where needed, scaling the server-side due to larger exponents, and limiting the amount of public metadata. Finally, I will provide a quick overview of the open-source Anonymous Tokens repository and discuss the parts that are not open-sourced.
{{% /expand %}}

### **17:00** *End of program*

## Organizers

- [Anna Weine](), *Mozilla*
- [Cindy Lin](https://cindylindeed.github.io/), *Google*
- [Fernando Lobato Meeser](), *Google*
- [Ioana Nedelcu](), *Google*
- [J.C. Jones](https://insufficient.coffee/about/), *Internet Security Research Group*

## Code of Conduct

All participants are expected to adhere to our [Community Guidelines](https://developers.google.com/community-guidelines). The event organizers will be available to address any Community Guideline breaches and may be reached at [organizers@oscwork.shop](mailto:organizers@oscwork.shop).

## Sponsors

*Google*
