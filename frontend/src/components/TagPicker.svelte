<script>
  /** Clickable suggestion chips that append/remove descriptors in a comma-separated text. */
  let { value = $bindable(''), groups } = $props();

  const parts = $derived(value.split(',').map((part) => part.trim()).filter(Boolean));
  const has = (tag) => parts.some((part) => part.toLowerCase() === tag.toLowerCase());

  function toggle(tag) {
    value = has(tag) ? parts.filter((part) => part.toLowerCase() !== tag.toLowerCase()).join(', ') : [...parts, tag].join(', ');
  }
</script>

<div class="groups">
  {#each Object.entries(groups) as [group, tags] (group)}
    <div class="group">
      <span class="muted">{group}</span>
      {#each tags as tag (tag)}
        <button type="button" class="chip" class:selected={has(tag)} onclick={() => toggle(tag)}>{tag}</button>
      {/each}
    </div>
  {/each}
</div>

<style>
  .groups { display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.5rem; }
  .group { display: flex; flex-wrap: wrap; gap: 0.35rem; align-items: center; }
  .group > span { font-size: 0.75rem; width: 80px; }
  .chip { padding: 0.2rem 0.65rem; font-size: 0.8rem; }
  .chip.selected { border-color: var(--accent); color: var(--accent); }
</style>
