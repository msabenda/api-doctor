const checks = ['Failure diagnosis', 'Security guidance', 'Copyable fixes']

export function App() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-16 text-slate-100">
      <section className="mx-auto max-w-4xl">
        <p className="mb-4 font-mono text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
          Developer-first API diagnostics
        </p>
        <h1 className="max-w-3xl text-5xl font-bold tracking-tight sm:text-7xl">
          API Doctor
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
          Understand why an API request failed and learn how to fix it securely.
        </p>
        <div className="mt-10 grid gap-4 sm:grid-cols-3">
          {checks.map((check) => (
            <article
              className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
              key={check}
            >
              <span aria-hidden="true" className="text-cyan-400">
                ✓
              </span>
              <h2 className="mt-3 font-semibold">{check}</h2>
            </article>
          ))}
        </div>
        <div className="mt-10 rounded-2xl border border-cyan-950 bg-cyan-950/30 p-5 text-cyan-100">
          The request workspace is coming next. Outbound requests stay disabled
          until SSRF controls are implemented and tested.
        </div>
      </section>
    </main>
  )
}
