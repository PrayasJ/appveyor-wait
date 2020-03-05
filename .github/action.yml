workflow "Test Wait for Appveyor" {
  on = "push"
  resolves = ["Wait for Appveyor"]
}

action "Not deleted" {
  uses = "actions/bin/filter@3c0b4f0e63ea54ea5df2914b4fabf383368cd0da"
  args = "not deleted"
}

action "Wait for Appveyor" {
  needs = ["Not deleted"]
  uses = "./wait-for-Appveyor"
}
