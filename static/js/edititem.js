document.querySelector('.content').addEventListener('submit', (event) => {
  event.preventDefault()
  const data = new FormData(event.target)
  const id = event.target.getAttribute('targetid')
  const request = new Request(`/api/item/${id}`, {
    method: 'patch',
    body: data
  })

  fetch(request).then(res => {
    if (res.ok) {
      window.location.replace('/dashboard')
    } else {
      alert('ERROR CREATING INGREDIENT')
    }
  }).catch(error => console.log('error:', error))
})