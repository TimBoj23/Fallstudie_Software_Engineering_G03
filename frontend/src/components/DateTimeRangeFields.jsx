export default function DateTimeRangeFields({ values, onChange, prefix = "" }) {
  function update(key, value) {
    onChange({ ...values, [`${prefix}${key}`]: value });
  }

  return (
    <div className="form-grid two">
      <label>
        <span>Start</span>
        <input
          type="datetime-local"
          value={values[`${prefix}start`] || ""}
          onChange={(event) => update("start", event.target.value)}
        />
      </label>
      <label>
        <span>Ende</span>
        <input
          type="datetime-local"
          value={values[`${prefix}end`] || ""}
          onChange={(event) => update("end", event.target.value)}
        />
      </label>
    </div>
  );
}
