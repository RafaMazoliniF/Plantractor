# Plantractor
A simple website to apply cloud development concepts.

## Network Architecture
Plantractor is served with 3 virtual machines running different services:
- **VM1**:
  - Runs a simple NGINX as reverse-proxy.
  - Connect to internet via NAT with the host.
  - Connect to the internal isolated network (VM2 and VM3) with a dedicated network port.

- **VM2**:
  - Runs the website service (both backend and frontend).
  - Connected just to the internal isolated network.
  - Access database service (served in VM3) by a gateway API.

- **VM3**:
  - Runs the database service providing a gateway API.
  - Connected just to the internal isolated network.
 
## Technologies
- **Reverse-Proxy**: NGINX;
- **Backend**: Flask;
- **Frontend**: HTML, CSS, JavaScript, Tailwind;
- **Database**: SQLite + Flask;
- **Virtualization Orchestrator**: Vagrant + libvirt

## Running the Project
**Prerequisites**: 
- Vagrant installed;
- LibVirt installed;
- Internet Access;

1. Access `./vagrant/` directory;
2. Run `vagrant up`;
