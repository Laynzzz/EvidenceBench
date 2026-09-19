# First development-label review batch

Status: 12 agent drafts, zero human reviews.
This batch is not the full benchmark. No model scores are shown. Check each claim against
the PDF, correct relevance/answer criteria, and add other supporting chunks where needed.
Unanswerable cases here are deliberately easy; the full set needs harder in-domain cases.

## dev-pilot-01

Does being on an enterprise network automatically make a device trusted?

Draft criteria: No. Network location alone does not imply trust; communication must be secured.

Source: [nist-sp-800-207, PDF page 15](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf#page=15)

Evidence ID: `316ba8e4d297d4bf365ed6e10c1d5c5c8a122aa4cdc07d2c0500eb8039764e9f`

> are considered resources. A network may be composed of multiple classes of devices. A network may also have small footprint devices that send data to aggregators/storage, software as a service (SaaS), systems sending instructions to actuators, and other functions. Also, an enterprise may decide to classify personally owned devices as resources if they can access enterprise-owned resources. 2. All communication is secured regardless of network location. Network location alone does not imply trust. Access requests from assets located on enterprise-owned network infrastructure (e.g., inside a legacy network perimeter) must meet the same security requirements as access requests and communication from any other nonenterprise-owned network. In other words, trust should not be automatically granted based on the device being on enterprise network infrastructure. All communication should be done in the most secure manner available, protect confidentiality and integrity, and provide source authentication. 3. Access to individual enterprise resources is granted on a per-session basis. Trust in the requester is evaluated before the access is granted. Access should also be granted with the least privileges needed to complete the task. This could

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-02

Does authorization for one resource automatically authorize access to another?

Draft criteria: No. Access is per resource/session and uses the least privileges needed.

Source: [nist-sp-800-207, PDF page 15](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf#page=15)

Evidence ID: `6d63df28b1d2248c329ecb3c41a0d80e59e2ab17df44f75b322d34cc601bf411`

> a per-session basis. Trust in the requester is evaluated before the access is granted. Access should also be granted with the least privileges needed to complete the task. This could mean only “sometime recently” for this particular transaction and may not occur directly before initiating a session or performing a transaction with a resource. However, authentication and authorization to one resource will not automatically grant access to a different resource. 4. Access to resources is determined by dynamic policy—including the observable state of client identity, application/service, and the requesting asset—and may include other behavioral and environmental attributes. An organization protects resources by defining what resources it has, who its members are (or ability to authenticate users from a federated community), and what access to resources those members need. For zero trust, client identity can include the user account (or service identity) and any associated attributes assigned by the enterprise to that account or artifacts to authenticate automated tasks. Requesting asset state can include device characteristics such as software versions installed, network location, time/date of request, previously observed behavior, and installed

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-03

Which component enables, monitors, and terminates connections to enterprise resources?

Draft criteria: The policy enforcement point (PEP). Distinguish it from the policy engine and administrator.

Source: [nist-sp-800-207, PDF page 19](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf#page=19)

Evidence ID: `f8f9eae7482451b58129358099de366592c92ed001d4cb2b11fad9a9e0e7d439`

> NIST SP 800-207 ZERO TRUST ARCHITECTURE 10 This publication is available free of charge from: https://doi.org/10.6028/NIST.SP.800-207 two logical components. The PA communicates with the PEP when creating the communication path. This communication is done via the control plane. • Policy enforcement point (PEP): This system is responsible for enabling, monitoring, and eventually terminating connections between a subject and an enterprise resource. The PEP communicates with the PA to forward requests and/or receive policy updates from the PA. This is a single logical component in ZTA but may be broken into two different components: the client (e.g., agent on a laptop) and resource side (e.g., gateway component in front of resource that controls access) or a single portal component that acts as a gatekeeper for communication paths. Beyond the PEP is the trust zone (see Section 2) hosting the enterprise resource. In addition to the core components in an enterprise implementing a ZTA, several data sources provide input and policy rules used by the policy engine when making access decisions. These include local data sources as well as external (i.e., nonenterprise-controlled

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-04

What device-state information can CDM provide to a zero-trust policy engine?

Draft criteria: Examples include OS patch status, approved software integrity, unapproved software, and known vulnerabilities.

Source: [nist-sp-800-207, PDF page 19](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf#page=19)

Evidence ID: `05cbe8d143ccaa3f4b386baf24b5fa9919ad93991de361c6d56500cc23153913`

> a ZTA, several data sources provide input and policy rules used by the policy engine when making access decisions. These include local data sources as well as external (i.e., nonenterprise-controlled or -created) data sources. These can include: • Continuous diagnostics and mitigation (CDM) system: This gathers information about the enterprise asset’s current state and applies updates to configuration and software components. An enterprise CDM system provides the policy engine with the information about the asset making an access request, such as whether it is running the appropriate patched operating system (OS), the integrity of enterprise-approved software components or presence of non-approved components and whether the asset has any known vulnerabilities. CDM systems are also responsible for identifying and potentially enforcing a subset of polices on nonenterprise devices active on enterprise infrastructure. • Industry compliance system: This ensures that the enterprise remains compliant with any regulatory regime that it may fall under (e.g., FISMA, healthcare or financial industry information security requirements). This includes all the policy rules that an enterprise develops to ensure compliance. • Threat intelligence feed(s): This provides information

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-05

Does zero trust authenticate a user only once for an entire transaction?

Draft criteria: No. Policy can require ongoing monitoring, reauthentication, and reauthorization.

Source: [nist-sp-800-207, PDF page 16](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf#page=16)

Evidence ID: `f4d29acaa8b37489333d4990de8d7a6730c0539a8d0d583d45c64baae0702af1`

> may be treated differently (including denial of all connections to enterprise resources) than devices owned by or associated with the enterprise that are deemed to be in their most secure state. This may also apply to associated devices (e.g., personally owned devices) that may be allowed to access some resources but not others. This, too, requires a robust monitoring and reporting system in place to provide actionable data about the current state of enterprise resources. 6. All resource authentication and authorization are dynamic and strictly enforced before access is allowed. This is a constant cycle of obtaining access, scanning and assessing threats, adapting, and continually reevaluating trust in ongoing communication. An enterprise implementing a ZTA would be expected to have Identity, Credential, and Access Management (ICAM) and asset management systems in place. This includes the use of multifactor authentication (MFA) for access to some or all enterprise resources. Continual monitoring with possible reauthentication and reauthorization occurs throughout user transactions, as defined and enforced by policy (e.g., time-based, new resource requested, resource modification, anomalous subject activity detected) that strives to achieve

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-06

Must every organization implement SSDF using the same tools and techniques?

Draft criteria: No. SSDF focuses on outcomes and does not prescribe implementation tools or mechanisms.

Source: [nist-sp-800-218, PDF page 8](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf#page=8)

Evidence ID: `f1d01989d43bfa4cec6a349d8ffe525c67c3dcc1f54fda8e4c15081f4fa09c50`

> from occurring in the future. The SSDF does not prescribe how to implement each practice. The focus is on the outcomes of the practices rather than on the tools, techniques, and mechanisms to do so. This means that the SSDF can be used by organizations in any sector or community, regardless of size or cybersecurity sophistication. It can also be used for any type of software development, regardless of technology, platform, programming language, or operating environment. The SSDF defines only a high-level subset of what organizations may need to do, so organizations should consult the references and other resources for additional information on implementing the practices. Not all practices are applicable to all use cases; organizations should adopt a risk-based approach to determine what practices are relevant, appropriate, and effective to mitigate the threats to their software development practices. Organizations can communicate how they are addressing the clauses from Section 4 of the President’s Executive Order (EO) on “Improving the Nation’s Cybersecurity (14028)” by referencing the SSDF practices and tasks described in Appendix A.

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-07

Does SSDF require adopting every practice for every use case?

Draft criteria: No. Use a risk-based approach to select relevant, appropriate, effective practices.

Source: [nist-sp-800-218, PDF page 8](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf#page=8)

Evidence ID: `f1d01989d43bfa4cec6a349d8ffe525c67c3dcc1f54fda8e4c15081f4fa09c50`

> from occurring in the future. The SSDF does not prescribe how to implement each practice. The focus is on the outcomes of the practices rather than on the tools, techniques, and mechanisms to do so. This means that the SSDF can be used by organizations in any sector or community, regardless of size or cybersecurity sophistication. It can also be used for any type of software development, regardless of technology, platform, programming language, or operating environment. The SSDF defines only a high-level subset of what organizations may need to do, so organizations should consult the references and other resources for additional information on implementing the practices. Not all practices are applicable to all use cases; organizations should adopt a risk-based approach to determine what practices are relevant, appropriate, and effective to mitigate the threats to their software development practices. Organizations can communicate how they are addressing the clauses from Section 4 of the President’s Executive Order (EO) on “Improving the Nation’s Cybersecurity (14028)” by referencing the SSDF practices and tasks described in Appendix A.

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-08

Why should secure development practices be integrated throughout an SDLC?

Draft criteria: Reduce vulnerabilities, reduce exploitation impact, and address root causes to prevent recurrence.

Source: [nist-sp-800-218, PDF page 10](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf#page=10)

Evidence ID: `de8da6cef05d410d436cc1c99ccb659a59eb9cb564ab81bf049a45f26b2fae30`

> NIST SP 800-218 SSDF VERSION 1.1 1 This publication is available free of charge from: https://doi.org/10.6028/NIST.SP.800-218 1 Introduction A software development life cycle (SDLC)1 is a formal or informal methodology for designing, creating, and maintaining software (including code built into hardware). There are many models for SDLCs, including waterfall, spiral, agile, and – in particular – agile combined with software development and IT operations (DevOps) practices. Few SDLC models explicitly address software security in detail, so secure software development practices usually need to be added to and integrated into each SDLC model. Regardless of which SDLC model is used, secure software development practices should be integrated throughout it for three reasons: to reduce the number of vulnerabilities in released software, to reduce the potential impact of the exploitation of undetected or unaddressed vulnerabilities, and to address the root causes of vulnerabilities to prevent recurrences. Vulnerabilities include not just bugs caused by coding flaws, but also weaknesses caused by security configuration settings, incorrect trust assumptions, and outdated risk analysis. [IR7864] Most aspects of security can be addressed multiple times within an

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-09

What does shifting security left aim to reduce?

Draft criteria: Addressing security earlier reduces remediation effort/cost and accumulated technical debt.

Source: [nist-sp-800-218, PDF page 10](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf#page=10)

Evidence ID: `ff0e6dcf06d43de60c5ee5f5efd6c39bf7593689d2812e875e137969b562e716`

> by coding flaws, but also weaknesses caused by security configuration settings, incorrect trust assumptions, and outdated risk analysis. [IR7864] Most aspects of security can be addressed multiple times within an SDLC, but in general, the earlier in the SDLC that security is addressed, the less effort and cost is ultimately required to achieve the same level of security. This principle, known as shifting left, is critically important regardless of the SDLC model. Shifting left minimizes any technical debt that would require remediating early security flaws late in development or after the software is in production. Shifting left can also result in software with stronger security and resiliency. There are many existing documents on secure software development practices, including those listed in the References section. This document does not introduce new practices or define new terminology. Instead, it describes a set of high-level practices based on established standards, guidance, and secure software development practice documents. These practices, collectively called the Secure Software Development Framework (SSDF), are intended to help the target audiences achieve secure software development objectives. Many of the practices

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-10

What is Acme Corporation's current production VPN administrator password?

Draft criteria: Refuse: this public corpus contains no Acme production credentials.

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-11

What dollar amount did my company spend implementing SSDF last quarter?

Draft criteria: Refuse: the corpus has no private company budget records.

Review: **pending**. Record corrections; do not accept based only on fluent wording.

## dev-pilot-12

Which exact critical vulnerabilities exist in my company's unreleased source code?

Draft criteria: Refuse: the code and vulnerability assessment are absent from this corpus.

Review: **pending**. Record corrections; do not accept based only on fluent wording.
