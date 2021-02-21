document.querySelector('.search-form').addEventListener('submit', event => {
  event.preventDefault()
  const query = document.querySelector('#search').value
  fetch(`/api/search/${query}`).then(res => {
    if (res.ok) {
      return res.json()
    } else {
      alert('Did not find any results')
    }
  }).then(json => {
    window.location.replace(`/viewitem/${json.id}`)
  }).catch(error => console.log(error))
})