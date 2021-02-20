document.querySelector('.content').addEventListener('submit', (event) => {
  event.preventDefault()
  const form = document.querySelector('.content')
  const data = new FormData(form)
  const request = new Request('/api/item', {
    method: 'post',
    body: JSON.stringify({
      restaurant: data.get('restaurant'),
      name: data.get('name'),
      description: data.get('description'),
      ingredients: data.get('ingredients'),
      image: data.get('image')
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  })

  fetch(request).then(res => {
    if (res.ok) {
      window.location.replace('/dashboard')
    } else {
      alert('ERROR CREATING INGREDIENT')
    }
  }).catch(error => console.log(error))
})
