const handleShowRestRegister = () => {
  document.querySelector('.control').classList.add('hide')
  document.querySelector('.rest-register').classList.remove('hide')
}

const handleHideRestRegister = () => {
  document.querySelector('.control').classList.remove('hide')
  document.querySelector('.rest-register').classList.add('hide')
}

const handleShowRestLogin = () => {
  document.querySelector('.control').classList.add('hide')
  document.querySelector('.rest-login').classList.remove('hide')
}

const handleHideRestLogin = () => {
  document.querySelector('.control').classList.remove('hide')
  document.querySelector('.rest-login').classList.add('hide')
}

const handleShowUserRegister = () => {
  alert('Coming Soon!')
}