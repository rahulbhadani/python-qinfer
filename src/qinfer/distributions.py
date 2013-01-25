#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# distributions.py: module for probability distributions
##
# © 2012 Chris Ferrie (csferrie@gmail.com) and
#        Christopher E. Granade (cgranade@gmail.com)
#     
# This file is a part of the Qinfer project.
# Licensed under the AGPL version 3.
##
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

## IMPORTS #####################################################################

import numpy as np
import scipy.linalg as la
import abc

## CLASSES #####################################################################

class Distribution(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def sample(self, n=1):
        pass

class UniformDistribution(Distribution):
    def __init__(self, ranges=np.array([[0, 1]])):
        if not isinstance(ranges, np.ndarray):
            ranges = np.array(ranges)
            
        if len(ranges.shape) == 1:
            ranges = ranges[np.newaxis, ...]
    
        self._ranges = ranges
        self._n_rvs = ranges.shape[0]
        self._delta = ranges[:, 1] - ranges[:, 0]
        
    def sample(self, n=1):
        shape = (n, self._n_rvs)# if n == 1 else (self._n_rvs, n)
        z = np.random.random(shape)
        return self._ranges[:, 0] + z * self._delta

    def grad_log_pdf(self, var):
        # TODO: This is not quite true
        return np.zeros(var.shape)

# TODO: make the following into Distributions.        
class HilbertSchmidtUniform(object):
    """
    Creates a new Hilber-Schmidt uniform prior on state space of dimension ``dim``.
    See e.g. [Mis12]_.

    :param int dim: Dimension of the state space.
    """
    def __init__(self,dim = 2):
        self.dim = dim

    def sample(self):
        #Generate random unitary (see e.g. http://arxiv.org/abs/math-ph/0609050v2)        
        g = (np.random.randn(self.dim,self.dim) + 1j*np.random.randn(self.dim,self.dim))/np.sqrt(2.0)
        q,r = la.qr(g)
        d = np.diag(r)
        
        ph = d/np.abs(d)
        ph = np.diag(ph)
        
        U = np.dot(q,ph)

        #Generate random matrix        
        z = np.random.randn(self.dim,self.dim) + 1j*np.random.randn(self.dim,self.dim)
        
        rho = np.dot(np.dot(np.identity(self.dim)+U,np.dot(z,z.conj().transpose())),np.identity(self.dim)+U.conj().transpose())
        rho = rho/np.trace(rho)
        
        z = np.real(np.trace(np.dot(rho,np.array([[1,0],[0,-1]]))))
        y = np.real(np.trace(np.dot(rho,np.array([[0,-1j],[1j,0]]))))
        x = np.real(np.trace(np.dot(rho,np.array([[0,1],[1,0]]))))
        
        return np.array([x,y,z])

class HaarUniform(object):
    """
    Creates a new Haar uniform prior on state space of dimension ``dim``.

    :param int dim: Dimension of the state space.
    """
    def __init__(self,dim = 2):
        self.dim = dim
    
    def sample(self):
        #Generate random unitary (see e.g. http://arxiv.org/abs/math-ph/0609050v2)        
        z = (np.random.randn(self.dim,self.dim) + 1j*np.random.randn(self.dim,self.dim))/np.sqrt(2.0)
        q,r = la.qr(z)
        d = np.diag(r)
        
        ph = d/np.abs(d)
        ph = np.diag(ph)
        
        U = np.dot(q,ph)
        
        #TODO: generalize this to general dimensions
        #Apply Haar random unitary to |0> state to get random pure state
        psi = np.dot(U,np.array([1,0]))
        z = np.real(np.dot(psi.conj(),np.dot(np.array([[1,0],[0,-1]]),psi)))
        y = np.real(np.dot(psi.conj(),np.dot(np.array([[0,-1j],[1j,0]]),psi)))
        x = np.real(np.dot(psi.conj(),np.dot(np.array([[0,1],[1,0]]),psi)))
        
        return np.array([x,y,z])

class GinibreUniform(object):
    """
    Creates a prior on state space of dimension dim according to the Ginibre
    ensemble with parameter ``k``.
    See e.g. [Mis12]_.
    
    :param int dim: Dimension of the state space.
    """
    def __init__(self,dim = 2, k = 2):
        self.dim = dim
        self.k = k
        
    def sample(self):
        #Generate random matrix        
        z = np.random.randn(self.dim,self.k) + 1j*np.random.randn(self.dim,self.k)
        
        rho = np.dot(z,z.conj().transpose())
        rho = rho/np.trace(rho)
        
        z = np.real(np.trace(np.dot(rho,np.array([[1,0],[0,-1]]))))
        y = np.real(np.trace(np.dot(rho,np.array([[0,-1j],[1j,0]]))))
        x = np.real(np.trace(np.dot(rho,np.array([[0,1],[1,0]]))))
        
        return np.array([x,y,z])
