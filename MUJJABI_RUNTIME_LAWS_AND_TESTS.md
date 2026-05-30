# Mujjabi Runtime Laws, Principles, and Tests

Last aligned: 2026-05-30

This file is the public naming layer for CDFD Runtime. It restores the runtime
law/test surface from the CDFD paper series and states how each claim is handled
by executable code, CLI output, or documented falsification criteria.

The names are strong by design, but their status is disciplined. A law here
means a law inside the CDFD framework or runtime model until independent
experiment, external benchmark, or domain-specific validation establishes a
stronger physical, biological, clinical, engineering, or historical status.

## Source Spine

This runtime file is aligned to:

- `CDFD-Part-I-Release/Part_I_Fundamental_Physics/MUJJABI_LAWS_AND_TESTS.md`
- `CDFD-Part-II-Release/Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/MUJJABI_LIFE_LAWS_AND_TESTS.md`
- `CDFD-Part-III-Release/MUJJABI_BIOLOGY_LAWS_AND_TESTS.md`
- `CDFD-Part-IV-Release/MUJJABI_UNIVERSAL_LAWS_AND_TESTS.md`

## Core Runtime Grammar

| Name | Symbolic form | Runtime meaning | Status |
|---|---|---|---|
| Mujjabi Adaptive Operating Ratio | `Psi_s = (Phi / C) * S * M_s` | Shared grammar for flow, constraint, responsiveness, and structural memory across runtime domains. | Core notation. |
| Mujjabi Capacity Law | `Phi / C -> 1` drives nonlinear regulation | Throughput becomes nonlinear near effective capacity. Runtime demos expose this as regime change, saturation, or overload. | CDFD law; empirical status open. |
| Mujjabi Runtime Constraint Law | `C > 0` and finite output required for accepted runs | Prevents division artifacts and non-finite values from entering public output as discoveries. | Runtime guardrail. |
| Mujjabi Finite-Audit Principle | `NaN`, `Inf`, and non-finite values block release output unless explicitly labeled as failed diagnostics | Every public envelope carries a finite audit. | Release guardrail. |
| Mujjabi Domain Adapter Principle | Domain variables must map explicitly into `Phi`, `C`, `S`, `M_s`, or declared diagnostics | Keeps cross-domain analogies inspectable and falsifiable. | Adapter contract. |
| Mujjabi CDFL Execution Principle | Model text must parse, execute, and emit structured provenance | CDFL models are reproducible from source files, not screenshots or prose. | Public software principle. |
| Mujjabi Provenance Principle | Every public result carries command, parameters, runtime, and timestamp context | Makes reruns and failures traceable. | Reproducibility rule. |
| Mujjabi Provider-Key Boundary Principle | Provider keys, user identity, hosted accounts, and workflow policy belong above deterministic execution | `cdfd llm` may call a provider for research interpretation only when runtime key material and a model are explicitly supplied. | Architecture principle. |
| Mujjabi Discovery-Triage Principle | Candidate discoveries select follow-up tests; they do not count as proof by themselves | Runtime outputs identify falsification targets and parameter windows. | Claim-discipline rule. |

## Part I Physics Laws Exposed Through Runtime

| Name | Symbolic form or condition | Runtime handle | Status |
|---|---|---|---|
| Mujjabi Stability Attractor | `chi = R/a = 1/alpha` | Used as a Part I theoretical target; runtime does not treat it as an external measurement. | Internal derivation / numerical target. |
| Mujjabi Vacuum Memory Law | `M_s -> 1` at low flux; `M_s != 1` after overload | Memory-bearing simulations and hysteresis probes test whether prior load leaves bounded residuals. | Proposed non-equilibrium law. |
| Mujjabi Hysteresis Kernel | `M_s(x,t)=1+mu integral max(0,Phi/C-1) exp(-(t-t')/tau_M) dt'` | Candidate memory kernel for pump-load and recovery-style protocols. | Falsifiable kernel. |
| Mujjabi Boundary Principle | Candidate states must survive topology, capacity, phase, and stability constraints | Runtime papers use it to reject arbitrary modes and unsupported discoveries. | Internal selection rule. |
| Mujjabi Geometric Charge Principle | Charge as vortex-core boundary discontinuity or surface-tension signature | Preserved as Part I hypothesis; runtime can only provide model diagnostics. | Hypothesis. |
| Mujjabi Action Principle | `h = Phi_c * tau_v` | Preserved as an open Part I derivation target, not a runtime proof. | Open derivation. |
| Mujjabi Vacuum Engineering Principle | Control `Phi`, `C`, `S`, or `M_s` to move a system across `Psi_s=1` | Runtime demos expose controllable variables and response curves for later experiments. | Future engineering program. |

## Part II Life Laws Exposed Through Runtime

| Name | Symbolic form or condition | Runtime handle | Status |
|---|---|---|---|
| Mujjabi Origin Constraint Law | `Psi_s=(Phi/C) S M_s` | Origins-of-life demos require drive, constraint, routing, and retained memory to reinforce together. | Core notation / derived framing. |
| Mujjabi Geochemical Coupling Principle | Redox or mineral conductance must terminate in chemistry | Runtime source-mix and endpoint diagnostics remain follow-up selectors, not wet-lab proof. | Experimental guardrail. |
| Mujjabi Proton Coherence Gate | `C_ep > 0` for overlapping electron and proton or ion currents | Preserved as a coupling metric for future lab protocols. | Hypothesis / testable coupling metric. |
| Mujjabi Polymerization Ratchet | `M_s(t+nT) > M_s(t)` over cycles | Runtime cycle language treats retention across cycles as the relevant memory signal. | Hypothesis. |
| Mujjabi Chemical Memory Law | `Gamma_closure > 1` is necessary but not sufficient | Closure begins memory only when amplification beats loss and persists through cycles. | CDFD law; empirical status open. |
| Mujjabi Alphabet Stability Principle | `K_pat` must exceed degradation noise | Pattern persistence must survive flux noise before symbolic chemistry claims are made. | Hypothesis. |
| Mujjabi Boundary Covariance Principle | `Cov(internal state, container persistence) > 0` | Protocell claims require internal chemistry to affect boundary survival or division. | Derived protocell criterion. |
| Mujjabi Parasitic Threshold | `host gate > parasite access` | Runtime host-parasite models must include specificity, exclusion, repair, or degradation when copying appears. | Hypothesis / falsifiable mechanism. |
| Mujjabi Life Number | `Lambda_life = I_E sigma_e sigma_p tau_relax / (B_stab E_maintenance)` | Runtime diagnostics expose decay, near-critical, and sustained-persistence regimes. | Derived synthesis. |

## Part III Biology and Medicine Translations

These are proposed biological translations, not validated clinical biomarkers.
They must not be used as medical advice.

| Name | Runtime meaning | Testable direction | Status |
|---|---|---|---|
| Mujjabi Biology Capacity Law | Tissue, pathway, or system throughput becomes nonlinear when sustained flow approaches effective capacity. | Increasing input stops improving output once the constraint marker rises. | Translation hypothesis. |
| Mujjabi Constraint Memory Law | Prior load can persist in `M_s` as fibrosis, epigenetic locking, chronic inflammation, remodeling, or scarring. | Equal current load recovers more slowly when prior stress burden is higher. | Translation hypothesis. |
| Mujjabi Boundary-Covariance Test | Internal flow and boundary integrity covary in healthy systems. | Combined flow and barrier markers outperform either marker alone. | Candidate validation test. |
| Mujjabi Parasitic-Drain Test | A high-flow, low-response lesion or node can drain surrounding capacity. | Local high-flow, low-response sites predict systemic burden or resistance. | Candidate validation test. |
| Mujjabi Cycling-Retention Test | Repeated stress-recovery cycles can lower or lock maladaptive memory depending on amplitude and recovery time. | Equal total load with different timing produces different `M_s` and `Psi_s` trajectories. | Candidate validation test. |
| Mujjabi Pharmacological Orthogonality Test | Cross-axis therapies may perform better than redundant same-axis forcing. | Source-flow, constraint, relaxation, and boundary-response axes separate useful from plateauing combinations. | Candidate validation test. |

Candidate medicine metrics from Part III remain hypothesis targets: `CRI`,
`CRHT`, `MAOS`, `BES`, `MLI`, and `COCT`. Each needs context of use, measurable
proxy, expected direction, failure condition, and validation dataset before it
can move beyond hypothesis status.

## Part IV Universal Translations

| Name | Runtime meaning | Testable direction | Status |
|---|---|---|---|
| Mujjabi Universal Capacity Law | Any mapped system can become nonlinear when sustained flow approaches effective capacity. | Input stops improving output once the dominant constraint proxy rises faster than recovery. | Universal translation; open empirical status. |
| Mujjabi Universal Memory Law | Systems can retain prior load in `M_s`, including ecological degradation, infrastructure fatigue, institutional backlog, immune priming, physical hysteresis, or entrenched priors. | Equal current load recovers more slowly with greater prior stress history. | Universal translation; open empirical status. |
| Mujjabi Cross-Domain Isomorphism Test | Two domains may share CDFD form without sharing material mechanism. | Explicitly mapped flow, constraint, responsiveness, and memory proxies show comparable overload or recovery curves. | Model-level comparison. |
| Mujjabi Constraint-Relaxation Test | Recovery depends on `beta`, the effective constraint relaxation rate. | Faster recovery capacity lowers peak `Psi_s` and shortens memory persistence. | Candidate validation test. |
| Mujjabi Adapter Stress Test | Runtime adapters must return finite outputs, explicit regimes, and stable JSON artifacts. | Non-finite outputs or uninterpretable regimes indicate runtime or modeling failure, not a discovery. | Runtime validation test. |
| Mujjabi Universal Cascade Test | A localized high-drive hub with slow relaxation can produce overload and memory locking in a network. | Changing drive, threshold, relaxation, or topology shifts the cascade boundary predictably. | Candidate diagnostic. |

## Mujjabi Runtime Tests

| Test | Prediction | Primary observable | Falsification condition |
|---|---|---|---|
| Mujjabi CLI Reproducibility Test | The same CDFL file and parameters produce the same structured result envelope. | `python cdfd.py run examples/heat_flow.cdfl` output. | Results change without source, parameter, or dependency changes. |
| Mujjabi CDFL Parse-Run Test | Valid CDFL parses into typed nodes and executes through the runtime executor. | Validation status, node count, and result blocks. | Valid syntax cannot be parsed or executed. |
| Mujjabi Domain Adapter Mapping Test | A registered domain maps payload values into bounded engine variables. | `python cdfd.py demo <domain>` final regime and finite audit. | Domain output is non-finite or lacks an inspectable mapping. |
| Mujjabi Finite Output Test | Public JSON output contains only finite, serializable values. | `finite_audit.all_finite == true`. | `NaN`, `Inf`, or unserializable values appear in output. |
| Mujjabi Provider-Key Boundary Test | Provider-key status and optional LLM research calls never print raw secrets and never enter deterministic engine state. | `cdfd llm status`, `cdfd llm explain`, and `cdfd auth` compatibility output. | A raw key appears in output, a status command calls a provider, or LLM output is treated as deterministic evidence. |
| Mujjabi Run Bundle Test | Saved runs carry result JSON, reports, manifest, provenance, and finite audit together. | `--save-run` output under `runs/`. | A saved result cannot be traced back to command, parameters, or artifacts. |
| Mujjabi Report-Explanation Test | Reports and explanations expose equations, interpretation, provenance, and claim boundaries. | `cdfd report` and `cdfd explain` outputs. | Reports omit source context, finite audit, or claim boundary language. |
| Mujjabi Doctor Surface Test | Public dependencies, domain registry, examples, web entrypoint, and finite-audit support are discoverable. | `python cdfd.py doctor --json`. | Critical checks fail in a clean public checkout. |
| Mujjabi Gallery Smoke Test | A curated set of domains produces finite, interpretable outputs through the same runtime envelope. | `python cdfd.py gallery --json`. | Core gallery rows are non-finite or lack explicit status/regime context. |

## Physics and Origins Falsification Tests

| Test | Prediction | Primary observable | Falsification condition |
|---|---|---|---|
| Mujjabi Vacuum Hysteresis Test | An intense pump pulse leaves a finite `M_s` residual before relaxation. | Probe-pulse phase or refractive residual decaying with `tau_M`. | No residual after QED, gas, optics, plasma, thermal, and detector effects are bounded. |
| Mujjabi Alpha-Jitter Test | Extreme flux environments perturb local vortex core behavior and produce alpha-sensitive residuals. | Non-QED residuals in high-field or high-Z spectra correlated with `Psi_s`. | Spectra remain fully explained by QED and known nuclear or field corrections. |
| Mujjabi Rotating-Source Test | Rapid angular momentum in dense sources changes a tiny pressure-gradient residual. | Atom-interferometer or torsion residual correlated with rotor angular momentum. | No residual beyond GR, Newtonian gravity, vibration, thermal, electromagnetic, and mechanical systematics. |
| Mujjabi Decoherence-Memory Test | Controlled systems show preparation-history-dependent coherence loss after standard channels are modeled. | Phase or visibility residual after prior flux loading. | Decoherence is exhausted by standard open-system terms. |
| Mujjabi Transport-Threshold Test | Friction, jamming, plasma, superconducting, and rupture transitions improve when written as adaptive capacity thresholds. | Transition timing, hysteresis loop, or avalanche threshold. | Established domain models predict the same data with equal or better residuals and no CDFD state variable. |
| Mujjabi Fe-S Endpoint Test | Connected Fe-S or mineral redox interfaces alter downstream products under matched feeds. | Endpoint product distribution between connected and disconnected reactors. | Product distributions do not differ after surface area, pH, redox, and residence time are controlled. |
| Mujjabi Mixed-Valence Bridge Test | Mixed-valence mineral networks improve source-sink redox coupling only when they form spanning graphs. | Conductance, redox-state transfer, and endpoint chemistry. | Conductance occurs without chemical endpoint benefit. |
| Mujjabi Proton-Coupling Test | Productive chemistry tracks spatial overlap of electron and proton or ion currents. | Coupling score, pH persistence, and product yield. | Electron and proton or ion overlap does not improve chemistry beyond uncoupled controls. |
| Mujjabi Ratchet Cycle Test | Repeated wet-dry, thermal, freeze-thaw, or pore cycles increase retained product memory in a finite window. | Product-length distribution and survival across cycles. | Cycling never outperforms steady controls across plausible activation and retention windows. |
| Mujjabi Closure-Ignition Test | Autocatalytic networks cross from sub-ignition to persistence only inside constrained parameter regions. | Bifurcation map in rate, feedstock, constraint, length, and loss. | Apparent closure vanishes under dilution, side reactions, or timestep refinement. |
| Mujjabi Aromatic Source-Mix Test | Terrestrial and exogenous aromatic feedstocks help only through retention and coupling. | `runtime.diagnostics.aromatic_source_mix_scenarios()` and `cdfd.py demo origins_of_life`. | Exogenous supply performs equally well without localization, or the best row changes without documented parameter updates. |
| Mujjabi Boundary-Covariance Test | Protocell candidates become selectable only when internal chemistry covaries with boundary persistence. | Covariance between copied internal state and growth, division, or retention. | Containers divide or persist independently of internal chemistry. |
| Mujjabi Parasitic-Drain Test | Noncontributing replicators collapse cooperative persistence unless specificity or exclusion is introduced. | Host-parasite ratio with controlled boundary access. | Parasite access does not change cooperative persistence under matched resources. |
| Mujjabi Photochemical Overload Test | Energy capture helps only when stabilization prevents destructive overload. | Capture yield, damage markers, recovery, and retained chemistry. | Extra light always damages or always helps independently of buffering capacity. |
| Mujjabi Dependency-Gate Test | A candidate origin setting must occupy a finite near-critical band rather than a single privileged point. | Joint map of drive, constraint, routing, and retained memory. | Any one variable alone predicts persistence as well as the coupled gate. |
| Mujjabi Spatial Parasite-Gate Test | Boundary specificity remains protective in spatial diffusion models, not only well-mixed equations. | Host-parasite ratio inside bounded compartments under matched resource inflow. | Spatial leakage eliminates the claimed host-retention advantage. |
| Mujjabi Photochemical Endpoint Test | Chlorophyll and eumelanin are mature endpoints, not origin requirements. | `photochemical_material_status()` in runtime diagnostics. | Endpoint language is used as proof of prebiotic necessity. |
| Mujjabi Life Number Boundary Test | Origins-of-life diagnostics occupy a finite near-critical band, not a single privileged point. | Life-number sweep output and runtime diagnostics. | Any single variable predicts persistence as well as the coupled gate. |

## Engineering Meaning

Runtime engineering means controlled manipulation of CDFD state variables and
careful measurement of discriminating responses. It does not mean immediate
technology, clinical deployment, or safety certification.

| Variable | Runtime or experimental handle | Observable |
|---|---|---|
| `Phi` or `J` | field intensity, drive, current, shear, angular momentum, redox feed, thermal gradient, UV/visible light, chemical activation | flux, phase, spectral, product-yield, or transport response |
| `C` | material boundary, confinement geometry, topology, pore geometry, permeability, surface charge, medium density | threshold shift, capacity saturation, residence time, or boundary retention |
| `S` | response surface, susceptibility, catalytic surface, adaptive routing, relaxation channel, phase-separated matrix | altered slope, selectivity, compliance, productive response, or recovery curve |
| `M_s` | prior loading, pulse history, copied sequence, retained product distribution, boundary composition, hysteresis protocol | memory residual, lag, persistence across cycles, inheritance, or recovery time `tau_M` |
| `B_stab` | radical buffers, photochemical screens, sacrificial redox sinks, overload protection | damage markers, overload recovery, and retained chemistry |

The design target is to steer a system toward, across, or away from
`Psi_s = 1` and measure a response that differs from established models. A
negative result is useful: it bounds or kills the relevant CDFD claim.

## Public Use Standard

Runtime output must stay attached to source files, commands, parameters,
provenance, finite audits, and failure conditions. A candidate law that cannot
be rerun, falsified, or compared against a baseline does not belong in the
public release surface.

LLM output, when requested through `cdfd llm explain`, is research
interpretation above deterministic runtime output. It is not engine evidence,
not validation, and not a substitute for the tests listed here.
