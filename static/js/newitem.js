document.querySelector('.content').addEventListener('submit', (event) => {
  event.preventDefault()
  const data = new FormData(event.target)
  const file = document.querySelector('#image-input').files[0]
  data.append('image', file, 'filename')
  const request = new Request('/api/item', {
    method: 'post',
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
