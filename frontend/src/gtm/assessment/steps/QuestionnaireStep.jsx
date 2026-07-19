import { useState } from 'react';

function RatingSlider({ scaleLabels, value, onChange }) {
  const current = value ?? 3;
  const label = scaleLabels[String(current)] ?? scaleLabels[current];

  return (
    <div>
      <input
        type="range"
        min={1}
        max={5}
        step={1}
        value={current}
        onChange={(event) => onChange(Number(event.target.value))}
        className="w-full accent-blue-700"
      />
      <div className="mt-1 flex justify-between text-[11px] text-slate-400">
        <span>1</span>
        <span>2</span>
        <span>3</span>
        <span>4</span>
        <span>5</span>
      </div>
      <div className="mt-4 rounded-lg bg-slate-50 p-4">
        <div className="text-xs font-semibold uppercase tracking-wide text-blue-700">Rating {current} of 5</div>
        <div className="mt-1 text-sm text-slate-700">{label}</div>
      </div>
    </div>
  );
}

export default function QuestionnaireStep({ questions, answers, onChangeAnswer, onSubmit }) {
  const [index, setIndex] = useState(0);
  const question = questions[index];
  const isLast = index === questions.length - 1;
  // A rating slider always shows a value (defaults to the neutral midpoint), so navigation
  // is never blocked here - unlike a chip selector, there's no "unanswered" visual state.

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-3 text-sm text-slate-500">
        Question {index + 1} of {questions.length}
      </div>
      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-6">
        <h3 className="text-base font-semibold text-slate-900">{question.question_text}</h3>
        <div className="mt-5">
          <RatingSlider
            scaleLabels={question.scale_labels}
            value={answers[question.key]}
            onChange={(value) => onChangeAnswer(question.key, value)}
          />
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between">
        <button
          type="button"
          disabled={index === 0}
          onClick={() => setIndex((current) => Math.max(0, current - 1))}
          className="rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Previous
        </button>
        {isLast ? (
          <button
            type="button"
            onClick={onSubmit}
            className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-800"
          >
            Submit answers
          </button>
        ) : (
          <button
            type="button"
            onClick={() => setIndex((current) => Math.min(questions.length - 1, current + 1))}
            className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-800"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
