console.log('SCRIPT IS LIVE')

document.querySelector('.content').addEventListener('submit', (event) => {
  event.preventDefault()
  console.log(event)
  console.log('data:', event.formData)
  console.log('action:', event.action)
  return false
})

console.log('ready')